"""
functions for uploading data into start schema rdb
"""

from datetime import datetime
import logging

import psycopg

from src.setup import RA_CENTRE_TZ as TZ, get_s3_bucket
from src.parser import parse_data, parse_object_name
from src.download import get_object_names, get_json_data

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
        return unprocessed_object_names

    except psycopg.Error as e:
        logger.error(f"Error reading from Postgres {e}")
        return []
    except Exception:
        logger.exception("An unhandled exception occured")
        return []

def get_table_column_mapping(conn, schema="source"):
    """
    Returns:
        column_map: A dictionary that maps column names to their tables.
            Example:
            {
                'table1_col1': 'table1',
                'table1_col2': 'table1',
                'table2_col1': 'table2'
            }
    """
    query = f"""
        SELECT
            table_name,
            column_name
        FROM
            information_schema.columns
        WHERE table_schema = '{schema}'
            AND (CAST(dtd_identifier AS INT) > 1)
        ORDER BY table_name, column_name
    """

    try:
        cursor = conn.cursor()
        cursor.execute(query)

        results = cursor.fetchall()

        column_map = {}
        for table_name, column_name in results:
            if column_name not in column_map:
                column_map[column_name] = table_name

        return column_map

    except psycopg.Error as e:
        logger.error(f"Error reading from Postgres {e}")
        return []
    except Exception:
        logger.exception("An unhandled exception occured")
        return []

def restructure_data_for_tables(data, column_map):
    """
    Restructures the parsed data into a dictionary where keys are table names
    and values are lists of dictionaries, each representing a row for that table.

    Args:
        data: A list of dictionaries, where each dictionary is a flat
            key-value store containing data for one or more tables.
            Example:
            {'table1_col1': 'value1', 'table1_col2': 'value2', 'table2_colA': 'dataA'},
        column_map: A dictionary that maps table names to their column prefixes.
            This is crucial for determining which columns belong to which table.
            Example:
            {
                'table1_col1': 'table1',
                'table1_col2': 'table1',
                'table2_col1': 'table2'
            }
    Returns:
        A dictionary where keys are table names and values are dictionaries
        ready to be loaded to their appropriate tables
        Example:
        {
            'table1': {'col1': 'value1', 'col2': 'value2'},
            'table2': {'colA': 'dataA', 'colB': 'dataB', 'colC': 'dataC'},
            'table3': {'fieldX': 123, 'fieldY': 'abc'}
        }
    """
    #initialize outvar
    ret_var = {}
    for table_name in list(set(column_map.values())):
        ret_var[table_name] = {}

    #iterate through flat key value store
    for col_name, value in data.items():
        table_name = column_map.get(col_name)  # Get table name from mapping
        if table_name is not None:
            ret_var[table_name].update({col_name: value})

    return ret_var

def generate_insert_sql(data, id_col_name, table_name, schema="source"):
    """
    generalize method for generating insert into DDL
    """
    keys = "(" + ", ".join(list(data.keys())) + ")"
    values = tuple(data.values())
    values_spec_str = "(" + ", ".join(["%s" for _ in range(len(values))]) + ")"
    sql = f"""
        INSERT INTO {schema}.{table_name} {keys}
        VALUES {values_spec_str}
        RETURNING {id_col_name}
    """

    return sql, values

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
        sql, values = generate_insert_sql(
            data,
            id_col_name="facility_id",
            table_name="facilities",
            schema=schema)
        cursor.execute(sql, values)
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
        sql, values = generate_insert_sql(
            data,
            id_col_name="timeslot_id",
            table_name="timeslots",
            schema=schema)
        cursor.execute(sql, values)
        table_id = cursor.fetchone()[0]  # Get the generated ID

    return table_id

def load_slot_event(data,
    facility_id,
    timeslot_id,
    cursor,
    schema="source"):
    """
    Loads registration events data into the registration_slot_events table, 
    checking for duplicates.

    Args:
        data: A list of dictionaries containing timeslot attribuites
        facility_id: the facilities table foreign key
        timeslot_id: the timeslots table foreign key
        cursor: PostgreSQL database cursor object.
        schema: schema to upload to

    Returns:
        the event_id
    """

    table_id = None
    #get the most recent record matching facility and timeslot
    query = f"""
        SELECT event_id, num_people, scraped_datetime
        FROM {schema}.reservation_system_events
        WHERE 
            facility_id = {facility_id}
            AND timeslot_id = {timeslot_id}
            AND week_number = {data["week_number"]}
        ORDER BY scraped_datetime DESC
        LIMIT 1
    """
    cursor.execute(query)
    existing_slot_event = cursor.fetchone()

    if existing_slot_event:
        if existing_slot_event[2] >= data["scraped_datetime"]:
            raise ValueError(
                "Scraped Datetime must be greater than most recent previous matching record"
                )
        if existing_slot_event[1] == data["num_people"]:
            # if the number of people is the same as the previous most recent record,
            # then this is a duplicate so don't insert it
            table_id = existing_slot_event[0]
            to_insert = False
            logger.debug(f"slot_event '{data}' already exists with ID: {table_id}")
        else:
            # if the number of people has changed since the previous most recent record,
            # then something has happened! Store this updated record and get the generated table_id
            to_insert = True
    else:
        # if the record doesn't exist then we should create a brand new one
        to_insert = True

    if to_insert:
        #insert raw data
        data["inserted_datetime"] =  datetime.now(tz=TZ)
        data["facility_id"] = facility_id
        data["timeslot_id"] = timeslot_id
        sql, values = generate_insert_sql(
            data,
            id_col_name="event_id",
            table_name="reservation_system_events",
            schema=schema)
        cursor.execute(sql, values)
        table_id = cursor.fetchone()[0]  # Get the generated ID

    return table_id

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
    sql, values = generate_insert_sql(
        helper_data,
        id_col_name="object_name",
        table_name="helper_loaded_objects",
        schema=schema)
    object_name = cursor.execute(sql, values)

    return object_name

def load_single_record(data, column_map, cursor):
    """
    logic for loading a single record
    """
    #initialize data structure
    structured_data = restructure_data_for_tables(data, column_map)

    logger.debug("loading facilities data")
    facility_id = load_facility(structured_data["facilities"], cursor)
    logger.debug("loading timeslots data")
    timeslot_id = load_timeslot(structured_data["timeslots"], cursor)
    logger.debug("loading reservation_system_events data")
    event_id = load_slot_event(
        data=structured_data["reservation_system_events"],
        facility_id=facility_id,
        timeslot_id=timeslot_id,
        cursor=cursor)

    return facility_id, timeslot_id, event_id

def load_data(conn, server, write_to_db=True):
    """
    logic for loading all data. Data from each S3 object is loaded as a 
    single transaction
    """
    # pylint: disable=too-many-locals, too-many-branches
    logger.info("retreiving list of available S3 objects")
    s3_bucket = get_s3_bucket()
    objects_list = get_object_names(bucket=s3_bucket)
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
            logger.info(f"processing object {object_name}")
            scraped_datetime = parse_object_name(object_name=object_name)

            #for each object in the list, check to see if it's already in the db
            logger.info("retreiving single s3 object")
            data = get_json_data(bucket=s3_bucket, object_name=object_name)

            data_map = get_table_column_mapping(conn)
            ids_list = []

            try:
                #do some simple preprocessing of raw data and upload if requested
                logger.info(f"parsing and uploading {len(data)} data records for {object_name}")
                cursor = conn.cursor()
                for item in data:
                    data_line, scraped_datetime = parse_data(item, scraped_datetime)

                    if write_to_db:
                        ids = load_single_record(data_line, data_map, cursor)
                        ids_list.append(ids)

                #commit transactions from entire object together otherwise rollback
                if write_to_db:
                    _ = load_helper_data(object_name, cursor)
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
