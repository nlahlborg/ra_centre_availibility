"""
functions for uploading data into start schema rdb
"""
import logging
from datetime import datetime

import psycopg
from psycopg import sql

from src.parser import parse_data, parse_object_name, DataValidationError
from src.download import (
    get_facilities_ids_dict, get_timeslots_ids_dict,
    get_reservation_system_events_ids_dict
    )

logger = logging.getLogger(__name__)

# pylint: disable=broad-exception-caught
def get_list_of_unprocessed_object_names(
        object_names,
        conn,
        table="helper_loaded_objects",
        schema="helper"
        ):
    """
    query the helper table to see which objects have already been uploaded
    and return as a list all the objects which are (1) not in the db and (2) 
    newer than the most recent object.
    """
    try:
        # pylint: disable=line-too-long
        placeholder = ", ".join([f"('{x}', '{parse_object_name(x).strftime('%Y-%m-%d %H:%M:%S%z')}'::timestamptz)" for x in object_names])

        # SQL query to fetch object names from the database that are in the provided list.
        query = f"""
            WITH input_data AS (
                SELECT *
                FROM (
                    VALUES
                        {placeholder}
                ) AS t(object_name, scraped_datetime)
            ),
            existing_data AS (
                SELECT
                    object_name,
                    scraped_datetime
                FROM "{schema}".{table}
            ),
            max_datetime AS (
                SELECT
                    MAX(scraped_datetime) AS max_date
                FROM "{schema}".{table}
            )
            SELECT
                i.object_name,
                i.scraped_datetime
            FROM input_data i
            LEFT JOIN existing_data e ON i.object_name = e.object_name
            CROSS JOIN max_datetime m
            WHERE e.object_name IS NULL
            AND (m.max_date IS NULL OR i.scraped_datetime > m.max_date);
        """
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        unprocessed_object_names = [row[0] for row in result]
        ret_val = sorted(unprocessed_object_names)

    except psycopg.Error as e:
        logger.error(f"Error reading from Postgres {e}")
        ret_val = []
    except Exception:
        logger.exception("An unhandled exception occured in reading from helper table")
        ret_val = []

    return ret_val

def generate_insert_sql(data, id_col_name, table_name, schema="source"):
    """
    generalize method for generating insert into DDL
    """
    keys = "(" + ", ".join(list(data.keys())) + ")"
    values = tuple(data.values())
    values_spec_str = "(" + ", ".join(["%s" for _ in range(len(values))]) + ")"
    stmt = f"""
        INSERT INTO {schema}.{table_name} {keys}
        VALUES {values_spec_str}
        RETURNING {id_col_name}
    """

    return stmt, values

def generate_insert_sql_batch(data_list, table_name, schema="source"):
    """
    generalize method for generating insert into DDL
    """
    first_row = data_list[0]
    columns = list(first_row.keys())
    placeholders = ', '.join(['%s'] * len(columns))
    table_id = sql.SQL("{}.{}").format(sql.Identifier(schema), sql.Identifier(table_name))
    stmt = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
        table_id,
        sql.SQL(', ').join(map(sql.Identifier, columns)),
        sql.SQL(placeholders)
    )

    values = [tuple(row[col] for col in columns) for row in data_list]

    return stmt, values

def load_slot_events_batch(data_list, cursor, schema="source"):
    """
    Loads reservation events data into the reservation_slot_events table, 

    Args:
        data: A list of dictionaries containing timeslot attribuites
        cursor: PostgreSQL database cursor object.
        schema: schema to upload to

    Returns:
        the event_id
    """
    try:
        #insert raw data
        stmt, values = generate_insert_sql_batch(
            data_list,
            table_name="reservation_system_events",
            schema=schema)
        cursor.executemany(stmt, values)

        #query the ids of the uploaded data
        query = f"""
            SELECT event_id
            FROM "{schema}".reservation_system_events
            ORDER BY event_id DESC
            LIMIT {len(data_list)}
            """
        cursor.execute(query)
        result = cursor.fetchall()
        event_ids = [x[0] for x in result[::-1]]
        
        return event_ids
    except psycopg.Error as e:
        logger.exception(e)
        return False

def load_helper_data(object_name, inserted_datetime, cursor, schema="helper"):
    """
    Loads object names data into the helper table

    Args:
        data: A list of dictionaries containing timeslot attribuites
        cursor: PostgreSQL database cursor object.
        schema: schema to upload to

    Returns:
        object name
    """
    if inserted_datetime is None:
        inserted_datetime = datetime.now()

    #insert object name record into helper table
    helper_data = {
        "object_name": object_name,
        "object_type": "raw_data",
        "scraped_datetime": parse_object_name(object_name),
        "inserted_datetime":  inserted_datetime
    }
    stmt, values = generate_insert_sql(
        helper_data,
        id_col_name="object_name",
        table_name="helper_loaded_objects",
        schema=schema)
    object_name = cursor.execute(stmt, values)

    return object_name

def load_single_data(data, table_name, id_col_name, cursor, schema="source"):
    """
    wrapper for generate_insert_sql and cursor.fetchone to insert 
    data and get the id of the inserted row

    Args:
        data: A list of dictionaries containing attributes
            (e.g., [{'facility_name': 'Badminton Court 1', 'facility_type': 'badminton_court'}]).
        table_name: name of the target table
        id_col_name: name of the id column to return
        cursor: PostgreSQL database cursor object.
        schema: schema to upload to

    Returns:
        the table_id
    """
    stmt, values = generate_insert_sql(data, id_col_name, table_name, schema)
    cursor.execute(stmt, values)
    table_id = cursor.fetchone()[0]  # Get the generated ID

    return table_id

def load_new_single_data(data, ids_dict, table_name, id_col_name, cursor, schema):
    """
    wrapper for load_single_data. Determines if the data is already in the db 
    and if not then uploads
    """
    # pylint: disable=too-many-arguments, too-many-positional-arguments
    #logger.info(f"getting {id_col_name} if it exists")
    idn = ids_dict.get(tuple(data.values()))
    if idn is None:
        #logger.info(f"uploading a new record to {table_name}:\n{data.values()}")
        idn = load_single_data(data, table_name, id_col_name, cursor, schema)
        ids_dict[tuple(data.values())] = idn
        #logger.info(f"The new id is {ids_dict[tuple(data.values())]}")

    return idn

def get_events_data_key(data):
    """
    create a tuple of the natural key for the reservation system events table
    """
    retval = (
        data.get("num_people"),
        data.get("week_number"),
        data.get("facility_id"),
        data.get("timeslot_id"),
    )

    return retval

def process_single_data(
        data,
        facilities_ids_dict,
        timeslots_ids_dict,
        events_table_ids_dict,
        cursor,
        scraped_datetime
    ):
    """
    process each data item from the s3 batch. If any new dimensions data are found
    they will be added to the db transaction as part of this function.

    returns a data item if the processed data is different from the most recent
    data row. Else it returns none.
    """
    # first parse the data
    #logger.info("parsing single line of data")
    facilities_data, timeslots_data, events_data = parse_data(data, scraped_datetime)

    # load the facility data if it is unique
    facility_id = load_new_single_data(
        data=facilities_data,
        ids_dict=facilities_ids_dict,
        table_name="facilities",
        id_col_name="facility_id",
        schema="source",
        cursor=cursor
    )

    # load the timeslot data if it is unique
    timeslot_id = load_new_single_data(
        data=timeslots_data,
        ids_dict=timeslots_ids_dict,
        table_name="timeslots",
        id_col_name="timeslot_id",
        schema="source",
        cursor=cursor
    )

    #include the ids in the events data row
    # logger.info("creating facts table data packet")
    events_data["facility_id"] = facility_id
    events_data["timeslot_id"] = timeslot_id
    events_data_key = get_events_data_key(events_data)
    if events_data_key not in events_table_ids_dict:
        ret_val = events_data
    else:
        ret_val = None

    return ret_val

def process_and_load_batch_data(data, object_name, conn, inserted_datetime=None, dry_run=False):
    logger.info(f"processing object {object_name}")
    scraped_datetime = parse_object_name(object_name=object_name)

    # load the existing tables from the db to compare in memory
    logger.info("loading db subsets")
    facilities_ids_dict = get_facilities_ids_dict(conn)
    timeslots_ids_dict = get_timeslots_ids_dict(conn)
    events_table_ids_dict = get_reservation_system_events_ids_dict(conn, min_start_datetime=scraped_datetime)

    # parse the raw data and store in memory
    logger.info(f"parsing and uploading {len(data)} data records for {object_name}")
    cursor = conn.cursor()
    events_data_list = []
    event_ids = []
    for item in data:
        events_data = process_single_data(
            data=item,
            scraped_datetime=scraped_datetime,
            facilities_ids_dict=facilities_ids_dict,
            timeslots_ids_dict=timeslots_ids_dict,
            events_table_ids_dict=events_table_ids_dict,
            cursor=cursor
        )

        if events_data is not None:
            if inserted_datetime is not None:
                events_data["inserted_datetime"] = inserted_datetime
            events_data_list.append(events_data)

    #batch upload of the facts table data
    if events_data_list:
        logger.info(f"batch uploading {len(events_data_list)} new records to the facts table")
        event_ids += load_slot_events_batch(events_data_list, cursor)
        #update the events natural key dict
        for idx in range(len(event_ids)):
            print(f"idx: {idx}, event_ids: {event_ids[idx]}")
            print(events_data_list[idx])
            events_table_ids_dict[get_events_data_key(events_data_list[idx])] = event_ids[idx]    
    else:
        logger.info("There is no new data to add from this batch.")
    logger.info("upating the helper table")
    _ = load_helper_data(object_name, inserted_datetime, cursor)

    #commit transactions from entire object together otherwise rollback
    if dry_run:
        cursor.close()
        conn.rollback()
        logger.info(f"DRY RUN: did not commit data for {object_name}")
    else:
        logger.info("committing batch")
        cursor.close()
        conn.commit()
        logger.info(f"uploaded data for {object_name}")

    return event_ids