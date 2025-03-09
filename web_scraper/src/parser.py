from datetime import datetime
import pytz
from typing import List, Dict, Any
import logging
import re

from src.setup import DB_TZ

DataObject = List[Dict[str, Any]]

logger = logging.getLogger("data_parser")

def parse_availability_data(data: DataObject) -> DataObject | None:
    """
    Parses availability data from a json_object and returns a Pandas DataFrame.

    Args:
        data: the json_object containing the availability data.

    Returns:
        A Pandas DataFrame with the specified columns, or None if an error occurs.
    """
    
    data_list = []
    for item in data:
        try:
            schedule = item.get("schedule")  # Get the schedule (might be None)
            if schedule and isinstance(schedule, list) and schedule:  # Check if schedule exists, is list and is not empty
                schedule_item = schedule[0] # Get the first schedule item.
                start_datetime = datetime.fromtimestamp(schedule_item["startDatetime"] / 1000) if schedule_item.get("startDatetime") else None
                end_datetime = datetime.fromtimestamp(schedule_item["endDatetime"] / 1000) if schedule_item.get("endDatetime") else None
            else:
                start_datetime = None
                end_datetime = None

            data_line = {
                "display_name": item.get("name"),
                "code": item.get("code"),
                "facility_name": item.get("facilityName"),
                "start_datetime": start_datetime,
                "end_datetime": end_datetime,
                "num_people": item.get("numPeople"),
                "has_reg_ended": item.get("hasRegEnded"),
                "inserted_datetime": datetime.now().astimezone(DB_TZ)
            }

            #make the unique slot id
            this_year = datetime.now(tz=pytz.timezone("US/Eastern")).year
            date_str = datetime.strptime(
                item.get("name").split("- ", maxsplit=1)[-1], r"%A %b %d - %I:%M %p"
                ).replace(year=this_year).strftime("%Y%m%d%H%M")
            slot_id = date_str + "_" + item.get("facilityName").lower().replace(" ", "_")
            
            data_line["slot_id"] = slot_id

            #get the facility type
            facility_type = "".join(re.findall("[a-z -]*", item.get("facilityName").lower())).strip()
            data_line["facility_type"] = facility_type

            data_list.append(data_line)

        except (ValueError, TypeError) as e:
            logger.warning(f"Error processing item: {item.get('name')}. Error: {e}")
            continue

    if data_list:
        return data_list
    else:
        return None