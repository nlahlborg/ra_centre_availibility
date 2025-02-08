import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging


logger = logging.getLogger("data_parser")

def parse_availability_data(data: List[Dict[str, Any]]) -> pd.DataFrame | None:
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

            sub_df = pd.DataFrame({
                "facility_name": item.get("facilityName"),
                "start_datetime": start_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                "end_datetime": end_datetime.strftime("%Y-%m-%d %H:%M:%S"),
                "num_people": item.get("numPeople"),
                "has_reg_ended": item.get("hasRegEnded"),
                "inserted_datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }, index=[0])
            data_list.append(sub_df)

        except (ValueError, TypeError) as e:
            logger.warning(f"Error processing item: {item.get('name')}. Error: {e}")
            continue

    if data_list:
        df = pd.concat(data_list).reset_index(drop=True)
        return df
    else:
        return None