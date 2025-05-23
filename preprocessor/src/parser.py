"""
web_scraper.src.parser

This module provides functions to parse availability data from the RA Centre website.
The data is parsed from a JSON object and transformed into a list of dictionaries
with specific columns. The module also includes helper functions to generate unique
slot IDs and determine facility types.
"""

from datetime import datetime, timedelta
import re
import logging

from src.setup import API_TZ, WEB_DISPLAY_TZ, DB_TZ

logger = logging.getLogger("data_parser")

class DataValidationError(Exception):
    """
    raise this exception if invalid data is detected while parsing
    """

def get_tz_aware_datetime(timestamp: int, tz=API_TZ) -> datetime:
    """
    converts a timestamp to timezone aware datetime
    """
    return datetime.fromtimestamp(int(timestamp/1000), tz=tz)

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

def parse_object_name(object_name, prefix="raw_centre_raw_", tz=DB_TZ):
    """
    extract the date strong from the object name

    Args:
        object_name (str): the object name from S3
        prefix (str): the prefix that comes before the date info

    """
    try:
        date_string = object_name.split(prefix)[-1]
        date_string = date_string.split(".json")[0]
        return tz.localize(datetime.strptime(date_string, "%Y%m%dT%H%M%SZ"))

    except ValueError as e:
        logger.error(f"received incorrectly formatted object name {object_name}")
        raise e

def parse_displayname(display_name:str, year: int, display_tz=WEB_DISPLAY_TZ) -> datetime:
    """
    get the datetime from the displayname
    """
    # split string based on "-" and " "
    parts = display_name.split('-')
    date_part = parts[1].strip().split(' ', maxsplit=1)[-1].strip()
    time_part = parts[2].strip()

    # Parse the datetime string
    datetime_str = f"{date_part} {year} {time_part}"
    retvar = display_tz.localize(datetime.strptime(datetime_str, "%b %d %Y %I:%M %p"))

    return retvar

def flag_inconsistant_datetime(start_datetime: datetime, display_name: str) -> None:
    """
    parse the reservation slot displayname and raise a DataValidationError if
    the displayname doesn't match the start_datetime
    """
    start_datetime_display = parse_displayname(display_name, start_datetime.year)
    if start_datetime_display != start_datetime:
        logger.error(f"start datetime from api parsing: {start_datetime} and displayname {display_name} are inconsistent.")
        raise DataValidationError

def flag_stale_start_datetime(start_datetime: datetime, scraped_datetime: datetime) -> None:
    """
    raise a DataValidationError if the start datetime is stale by more than 1 day
    """
    if  (scraped_datetime - start_datetime) > timedelta(days=1):
        logger.error(f"reservation slot start_datetime {start_datetime} is less than the scraped_datetime {scraped_datetime}, which is invalid")
        raise DataValidationError

def parse_data(data: dict, scraped_datetime: datetime) -> dict | None:
    """
    Parses availability data from a json_object and returns a Pandas DataFrame.

    Args:
        data: a single json-like object from the ra-centre api

    Returns:
        a flat key-value dict
    """
    display_name = data.get("name")
    schedule = data.get("schedule")  # Get the schedule (might be None)
    # Check if schedule exists, is list and is not empty
    if schedule and isinstance(schedule, list) and schedule:
        schedule_item = schedule[0] # Get the first schedule item.
        if schedule_item.get("startDatetime"):
            start_datetime = get_tz_aware_datetime(schedule_item["startDatetime"], tz=API_TZ)
        else:
            start_datetime = None
        if schedule_item.get("endDatetime"):
            end_datetime =get_tz_aware_datetime(schedule_item["endDatetime"])
        else:
            end_datetime = None
    else:
        start_datetime = None
        end_datetime = None

    facilities_data = {
        "facility_name": data.get("facilityName"),
        "facility_type": get_facility_type(data.get("facilityName")),
        }

    timeslot_data = {
        "start_time": start_datetime.astimezone(DB_TZ).timetz(),
        "end_time": end_datetime.astimezone(DB_TZ).timetz(),
        "day_of_week": start_datetime.astimezone(DB_TZ).strftime("%A"),
        "release_interval_days": (
            start_datetime - get_tz_aware_datetime(data.get("regStart"), tz=API_TZ)).days
    }

    event_data = {
        "num_people": data.get("numPeople"),
        "scraped_datetime": scraped_datetime.astimezone(DB_TZ),
        "week_number": start_datetime.astimezone(DB_TZ).isocalendar()[1]
    }

    #error checking
    flag_inconsistant_datetime(start_datetime, display_name)
    flag_stale_start_datetime(start_datetime, scraped_datetime)

    return facilities_data, timeslot_data, event_data
