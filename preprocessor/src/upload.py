"""
functions for uploading data into start schema rdb
"""

from datetime import datetime
import logging

import psycopg
from psycopg import sql

from src.setup import RA_CENTRE_TZ as TZ, get_s3_bucket
from src.parser import parse_data, parse_object_name
from src.download import (get_s3_object_names, get_s3_json_data,
    get_sql_facilities_table, get_sql_timeslots_table,
    get_sql_registration_system_events_table)

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
        return sorted(unprocessed_object_names)

    except psycopg.Error as e:
        logger.error(f"Error reading from Postgres {e}")
        return []
    except Exception:
        logger.exception("An unhandled exception occured")
        return []

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
    qualified_table_name = sql.SQL("{}.{}").format(sql.Identifier(schema), sql.Identifier(table_name))
    stmt = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
        qualified_table_name,
        sql.SQL(', ').join(map(sql.Identifier, columns)),
        sql.SQL(placeholders)
    )

    values = [tuple(row[col] for col in columns) for row in data_list]

    return stmt, values

def load_facility(data, cursor, schema="source"):
    """
    Loads facility data into the facilities table, checking for duplicates.

    Args:
        data: A list of dictionaries containing facility attributes
            (e.g., [{'facility_name': 'Badminton Court 1', 'facility_type': 'badminton_court'}]).
        cursor: PostgreSQL database cursor object.
        schema: schema to upload to

    Returns:
        the facility_id
    """
    table_id = None
    # Check if the facility already exists based on its name
    query = f"""
        SELECT facility_id
        FROM {schema}.facilities
        WHERE facility_name = '{data['facility_name']}'"""
    cursor.execute(query)
    existing_facility = cursor.fetchone()

    if existing_facility:
        # Facility already exists, return its ID
        table_id = existing_facility[0]
        logger.debug(f"Facility '{data['facility_name']}' already exists with ID: {table_id}")
    else:
        # Facility does not exist, insert it, and get the generated ID
        stmt, values = generate_insert_sql(
            data,
            id_col_name="facility_id",
            table_name="facilities",
            schema=schema)
        cursor.execute(stmt, values)
        table_id = cursor.fetchone()[0]  # Get the generated ID

    return table_id

def load_timeslot(data, cursor, schema="source"):
    """
    Loads timeslots data into the timeslots table, checking for duplicates.

    Args:
        data: A list of dictionaries containing timeslot attribuites
        cursor: PostgreSQL database cursor object.
        schema: schema to upload to

    Returns:
        the timeslot id
    """

    table_id = None
    # Check if the timeslot already exists based on its name
    query = f"""
        SELECT timeslot_id
        FROM {schema}.timeslots
        WHERE 
            start_time = '{data['start_time']}'
            AND end_time = '{data['end_time']}'
            AND day_of_week = '{data['day_of_week']}'
            AND release_interval_days = '{data['release_interval_days']}'
    """
    cursor.execute(query)
    existing_facility = cursor.fetchone()

    if existing_facility:
        # Facility already exists, return its table_id
        table_id = existing_facility[0]
        logger.debug(f"Timeslot '{data}' already exists with table_id: {table_id}")
    else:
        # Facility does not exist, insert it, and get the generated table_id
        stmt, values = generate_insert_sql(
            data,
            id_col_name="timeslot_id",
            table_name="timeslots",
            schema=schema)
        cursor.execute(stmt, values)
        table_id = cursor.fetchone()[0]  # Get the generated ID

    return table_id

def load_slot_events_batch(data_list, cursor, schema="source"):
    """
    Loads registration events data into the registration_slot_events table, 

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

        return True
    except psycopg.Error as e:
        logger.exception(e)
        return False


def load_helper_data(object_name, cursor, schema="helper"):
    """
    Loads object names data into the helper table

    Args:
        data: A list of dictionaries containing timeslot attribuites
        cursor: PostgreSQL database cursor object.
        schema: schema to upload to

    Returns:
        object name
    """

    #insert object name record into helper table
    helper_data = {
        "object_name": object_name,
        "object_type": "raw_data",
        "scraped_datetime": parse_object_name(object_name),
        "inserted_datetime":  datetime.now(tz=TZ)
    }
    stmt, values = generate_insert_sql(
        helper_data,
        id_col_name="object_name",
        table_name="helper_loaded_objects",
        schema=schema)
    object_name = cursor.execute(stmt, values)

    return object_name

def load_data(conn, server, dry_run=False, override_s3_bucket=False):
    """
    logic for loading all data. Data from each S3 object is loaded as a 
    single transaction
    """
    # pylint: disable=too-many-locals, too-many-branches
    inserted_datetime = datetime.now(tz=TZ)
    logger.info("retreiving list of available S3 objects")
    s3_bucket = get_s3_bucket(override_s3_bucket)
    objects_list = get_s3_object_names(bucket=s3_bucket)
    new_objects_list = get_list_of_unprocessed_object_names(objects_list, conn)

    if new_objects_list:
        logger.info(
            f"preparing to process {len(new_objects_list)} "
            f"new objects out of {len(objects_list)}."
            )
    else:
        logger.info("No new objects found. Will shut down.")
    try:
        for object_name in new_objects_list:
            # get the raw data from s3
            logger.info(f"processing object {object_name}")
            scraped_datetime = parse_object_name(object_name=object_name)
            logger.info("retreiving single s3 object")
            data = get_s3_json_data(bucket=s3_bucket, object_name=object_name)

            # load the dimensions tables from the db
            facilities_ids_dict = {tuple(row[1:]): row[0] for row in get_sql_facilities_table(conn)}
            timeslots_ids_dict = {tuple(row[1:]): row[0] for row in get_sql_timeslots_table(conn)}
            events_table_ids_dict = {tuple(row[1:]): row[0] for row in get_list_of_unprocessed_object_names(conn, scraped_datetime)}

            # parse the raw data and store in memory
            logger.info(f"parsing and uploading {len(data)} data records for {object_name}")
            cursor = conn.cursor()
            events_data_list = []
            try:
                for idx, item in enumerate(data):
                    #first parse the data
                    facilities_data, timeslot_data, events_data = parse_data(item, scraped_datetime)

                    #get the facilities id
                    facility_id = facilities_ids_dict.get(facilities_data)
                    if facility_id is None:
                        facility_id = load_facility(facilities_data, cursor)

                    #track unique timeslots:
                    timeslot_id = timeslots_ids_dict.get(timeslot_data)
                    if timeslot_id is None:
                        timeslot_id = load_timeslot(timeslot_data, cursor)

                    #include the ids in the events data row
                    events_data["facility_id"] = facility_id
                    events_data["timeslot_id"] = timeslot_id
                    events_data["inserted_datetime"] = inserted_datetime
                    events_data_key = (
                        events_data.get("num_people"), 
                        events_data.get("week_number"),
                        events_data.get("facility_id"), 
                        events_data.get("timeslot_id"),
                    )
                    if events_data_key not in events_table_ids_dict:
                        events_data_list.append(events_data)

                #batch upload of the facts table data
                load_slot_events_batch(events_data_list, cursor)
                _ = load_helper_data(object_name, cursor)

                #commit transactions from entire object together otherwise rollback
                if dry_run:
                    conn.rollback()
                    logger.info(f"DRY RUN: did not commit data for {object_name}")
                else:
                    conn.commit()
                    logger.info(f"uploaded data for {object_name}")

            except psycopg.Error as e:
                conn.rollback()
                logger.error(f"Error loading data: {e}")
            except KeyError as e:
                conn.rollback()
                logger.error(f"input data does not have the right format: {e}")
            except Exception:
                conn.rollback()
                logger.exception("An unhandled exception occured")
            finally:
                cursor.close()

        conn.close()
        if server:
            server.stop()

        return True
    except Exception:
        logger.exception("an unhandled exception occured ouside of the write transactions")
        conn.close()
        if server:
            server.stop()
        return False
