"""
functions to get data from s3
"""
import json
from json import JSONDecodeError
import logging

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

def get_s3_object_names(
        bucket,
        region_name: str='us-west-1'
        ):
    """
    get the object names from the listed s3 bucket, sorted ascending
    """

    try:
        client = boto3.client('s3', region_name=region_name)
        all_keys_returned = False
        object_names = []
        max_object_names = 10000
        marker = ""
        idx = 0
        while not all_keys_returned and len(object_names) < max_object_names and idx < 100:
            idx += 1 #loop exit safety
            response = client.list_objects(
                Bucket=bucket,
                MaxKeys = 1000,
                Marker=marker,
                Prefix='raw_centre_raw_'
            )
            if 'Contents' in response:
                partial_object_names = sorted([x.get('Key') for x in response["Contents"]])
                object_names += partial_object_names

                if len(partial_object_names) < 1000:
                    all_keys_returned = True
                else:
                    marker = partial_object_names[-1]

            else:
                all_keys_returned = True

        return sorted(object_names)

    except ClientError as e:
        logger.error(f"Error reading from S3: {e}")
        return []

def get_s3_json_data(bucket, object_name, region_name: str='us-west-1'):
    """
    get the specified object from s3
    """

    try:
        client = boto3.client('s3', region_name=region_name)

        response = client.get_object(
            Bucket=bucket,
            Key=object_name,
            )

        json_data = json.load(response.get("Body"))
        return json_data

    except ClientError as e:
        logger.error(f"Error reading from S3: {e}")
        return None
    except JSONDecodeError as e:
        logger.exception(f"Error decoding json: {e}")
        return None

def get_sql_facilities_table(conn, schema="source"):
    """
    fetch the facility SQL table
    """
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT
            facility_id,
            facility_name,
            facility_type
        FROM "{schema}".facilities
    """)
    data = cursor.fetchall()
    cursor.close()

    return data

def get_sql_timeslots_table(conn, schema="source"):
    """
    fetch the facility SQL table
    """
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT
            timeslot_id,
            start_time,
            end_time,
            day_of_week,
            release_interval_days
        FROM "{schema}".timeslots
    """)
    data = cursor.fetchall()
    cursor.close()

    return data

def get_sql_reservation_system_events_table(conn, min_start_datetime=None, schema="source"):
    """
    fetch the most recent event for each facility and timeslot combination
    """
    cursor = conn.cursor()

    if min_start_datetime is None:
        sql = f"""
            SELECT DISTINCT ON(facility_id, timeslot_id, week_number)
                event_id,
                num_people,
                week_number,
                facility_id,
                timeslot_id
            FROM "{schema}".reservation_system_events
            ORDER BY facility_id, timeslot_id, week_number, scraped_datetime DESC
        """
    else:
        sql = f"""
            SELECT DISTINCT ON(facility_id, timeslot_id, week_number)
                event_id,
                num_people,
                week_number,
                facility_id,
                timeslot_id
            FROM "{schema}".__reservation_system_events__start_datetime rse
            WHERE start_datetime >= ('{min_start_datetime}'::timestamp - '7 days'::interval)
            ORDER BY facility_id, timeslot_id, week_number, scraped_datetime DESC
        """

    cursor.execute(sql)
    data = cursor.fetchall()
    cursor.close()

    return data

def get_facilities_ids_dict(conn, schema="source"):
    """
    wrapper for get_sql_facilities_table
    returns a dictionary of unique table values
    """

    return {tuple(row[1:]): row[0] for row in get_sql_facilities_table(conn, schema)}

def get_timeslots_ids_dict(conn, schema="source"):
    """
    wrapper for get_sql_timeslots_table
    returns a dictionary of unique table values
    """
    return {tuple(row[1:]): row[0] for row in get_sql_timeslots_table(conn, schema)}

def get_reservation_system_events_ids_dict(conn, min_start_datetime=None, schema="source"):
    """
    wrapper for get_sql_reservation_system_events_table
    returns a dictionary of unique table values
    """
    table = get_sql_reservation_system_events_table(conn, min_start_datetime, schema)
    return {tuple(row[1:]): row[0] for row in table}
