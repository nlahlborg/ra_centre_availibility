"""
web_scraper.src.parser

This module provides functions to parse availability data from the RA Centre website.
The data is parsed from a JSON object and transformed into a list of dictionaries
with specific columns. The module also includes helper functions to generate unique
slot IDs and determine facility types.
"""

from datetime import datetime
import re
import logging

from src.setup import RA_CENTRE_TZ as TZ

logger = logging.getLogger("data_parser")

def get_tz_aware_datetime(timestamp: int, tz=TZ) -> datetime:
    """
    converts a timestamp to timezone aware datetime
    """
    return datetime.fromtimestamp(int(timestamp/1000), tz=TZ)

def get_facility_type(facility_name: str) -> str:
    """
    Determines the facility type based on the item data.

    The facility type is extracted from the facility name by converting it to lowercase,
    removing any non-alphabetic characters, and stripping leading and trailing spaces.

    Args:
        item (dict): The item data containing the facility name.

    Returns:
        str: The facility type.
    """
    facility_type = "".join(re.findall("[a-z -]*", facility_name.lower())).strip()
    facility_type = facility_type.replace(" ", "_")

    return facility_type

def parse_object_name(object_name, prefix="raw_centre_raw_"):
    """
    extract the date strong from the object name

    Args:
        object_name (str): the object name from S3
        prefix (str): the prefix that comes before the date info

    """
    try:
        date_string = object_name.split(prefix)[-1]
        date_string = date_string.split(".json")[0]
        return datetime.strptime(date_string, "%Y%m%dT%H%M%SZ").replace(tzinfo=TZ)

    except ValueError as e:
        logger.error(f"received incorrectly formatted object name {object_name}")
        raise e

def parse_data(data: dict, scraped_datetime: datetime) -> dict | None:
    """
    Parses availability data from a json_object and returns a Pandas DataFrame.

    Args:
        data: a single json-like object from the ra-centre api

    Returns:
        a flat key-value dict
    """
    try:
        schedule = data.get("schedule")  # Get the schedule (might be None)
        # Check if schedule exists, is list and is not empty
        if schedule and isinstance(schedule, list) and schedule:
            schedule_item = schedule[0] # Get the first schedule item.
            if schedule_item.get("startDatetime"):
                start_datetime = get_tz_aware_datetime(schedule_item["startDatetime"])
            else:
                start_datetime = None
            if schedule_item.get("endDatetime"):
                end_datetime =get_tz_aware_datetime(schedule_item["endDatetime"])
            else:
                end_datetime = None
        else:
            start_datetime = None
            end_datetime = None

        print(start_datetime)
        data_line = {
            "facility_name": data.get("facilityName"),
            "start_time": start_datetime.timetz(),
            "end_time": end_datetime.timetz(),
            "num_people": data.get("numPeople"),
        }

        data_line["facility_type"] = get_facility_type(data_line.get("facility_name"))
        data_line["week_number"] = start_datetime.isocalendar()[1]
        data_line["scraped_datetime"] = scraped_datetime
        data_line["inserted_datetime"] = datetime.now(tz=TZ)
        data_line["day_of_week"] = start_datetime.strftime("%A")
        data_line["release_interval_days"] = (
            start_datetime - get_tz_aware_datetime(data.get("regStart"))).days

        return data_line, scraped_datetime

    except (ValueError, TypeError, KeyError) as e:
        logger.warning(f"Error processing item: {data.get('name')}. Error: {e}") #pylint: disable=logging-fstring-interpolation
        return None, None
