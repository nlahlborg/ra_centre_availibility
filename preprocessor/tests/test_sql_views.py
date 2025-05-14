"""
test the logic in SQL views
"""
from datetime import datetime, timedelta
import sys
from pathlib import Path
sys.path.insert(1, str(Path(__file__).parent.parent))
import pytest

from tests.common import clear_starter_data
from src.setup import DB_TZ, WEB_DISPLAY_TZ
from src.upload import load_single_data

#from tests.helpers import VIEW__RESERVATION_SYSTEM_EVENTS__START_DATETIME_TEST_CONSTANT

# scraped_datetime,start_time,week_number,day_of_week,expected
VIEW__RESERVATION_SYSTEM_EVENTS__START_DATETIME_TEST_CONSTANT = (
    # base case Friday  Feb 07 - 3:00 PM (Ontario is EST)
    (
        DB_TZ.localize(datetime(2025, 1, 27, 0, 1, 0)),
        WEB_DISPLAY_TZ.localize(datetime(2025, 2, 7, 15, 0, 0)).astimezone(DB_TZ).timetz(),
        6,
        'Friday',
        WEB_DISPLAY_TZ.localize(datetime(2025, 2, 7, 15, 0, 0)).astimezone(DB_TZ)
    ),
    # troublesome case Saturday  Apr 26 - 5:00 PM (Ontario is EDT)
    (
        DB_TZ.localize(datetime(2025, 4, 26, 0, 2, 0)),
        WEB_DISPLAY_TZ.localize(datetime(2025, 4, 26, 17, 0, 0)).astimezone(DB_TZ).timetz(),
        17,
        'Saturday',
        WEB_DISPLAY_TZ.localize(datetime(2025, 4, 26, 17, 0, 0)).astimezone(DB_TZ)
    ),
    # happens at DST shift Sunday Mar 9 - 2:00 AM
    (
        DB_TZ.localize(datetime(2025, 3, 9, 1, 59, 0)),
        WEB_DISPLAY_TZ.localize(datetime(2025, 3, 9, 2, 0, 0)).astimezone(DB_TZ).timetz(),
        11,
        'Sunday',
        WEB_DISPLAY_TZ.localize(datetime(2025, 3, 9, 2, 0, 0)).astimezone(DB_TZ)
    ),


)

@pytest.mark.parametrize("scraped_datetime,start_time,week_number,day_of_week,expected", VIEW__RESERVATION_SYSTEM_EVENTS__START_DATETIME_TEST_CONSTANT)
def test__reservation_system_events__start_datetime(conn_fixture, scraped_datetime, start_time, week_number, day_of_week, expected):
    """
    clears the table and then tests that the start_datetime parser is giving the expected results
    """
    #set up data structures
    facilities_data = {
        "facility_name": "Badminton Court 1", 
        "facility_type": "badminton_court"
        }
    timeslots_data = {
        "start_time": start_time, 
        "end_time": start_time.replace(hour=start_time.hour + 1),
        "day_of_week": day_of_week,
        "release_interval_days": 7
        }
    reservation_system_events_data = {
        "num_people": 1,
        "scraped_datetime": scraped_datetime,
        "week_number": week_number,
        "facility_id": 1,
        "timeslot_id": 1
    }
    #clear all the tables
    cursor = conn_fixture.cursor()
    clear_starter_data(cursor)
    cursor.close()

    # insert data into the blank tables
    cursor = conn_fixture.cursor()
    _ = load_single_data(
        data=facilities_data,
        table_name="facilities",
        id_col_name="facility_id",
        cursor=cursor
    )
    _ = load_single_data(
        data=timeslots_data,
        table_name="timeslots",
        id_col_name="timeslot_id",
        cursor=cursor
    )
    _ = load_single_data(
        data=reservation_system_events_data,
        table_name="reservation_system_events",
        id_col_name="event_id",
        cursor=cursor
    )

    # query the view
    query = """
        SELECT start_datetime
        FROM source.__reservation_system_events__start_datetime
        LIMIT 1
    """
    cursor.execute(query)
    result = cursor.fetchone()[0]

    assert result == expected


