"""
a really specific integration type test to figure out this stubborn duplicates thing.
"""

import sys
from pathlib import Path
sys.path.insert(1, str(Path(__file__).parent.parent))

import pytest

from tests.common import clear_starter_data
from src.upload import process_and_load_batch_data
from src.download import get_facility_ids_dict, get_timeslot_ids_dict, get_reservation_system_events_ids_dict
from tests.helpers.raw_centre_raw_20250426T000200Z import json_data

from src.parser import parse_object_name
from tests.helpers.example_failed_upload import raw_json_path
scraped_datetime = parse_object_name(raw_json_path.name)

@pytest.mark.parametrize("min_datetime", (None, scraped_datetime))
def test_batch_upload_to_empty_db(conn_fixture, min_datetime):
    object_name = raw_json_path.name

    cursor = conn_fixture.cursor()
    clear_starter_data(cursor)
    cursor.close()
    event_ids_loaded = process_and_load_batch_data(
        data=json_data,
        object_name=object_name,
        conn = conn_fixture
        )

    assert len(json_data) == len(event_ids_loaded) 

    # all the loaded events should be in the events ids dict
    events_ids_dict =  get_reservation_system_events_ids_dict(conn_fixture, min_start_datetime=min_datetime)
    assert all([x in event_ids_loaded for x in events_ids_dict.values()])

    #all the facilities ids should also be in the events_ids_dict
    facility_ids_dict = get_facility_ids_dict(conn_fixture)
    facility_ids_in_events_ids_dict = [tup[2] for tup in events_ids_dict]
    assert all([x in facility_ids_in_events_ids_dict for x in facility_ids_dict.values()])

    #all the timeslots ids should also be in the events_ids_dict
    timeslot_ids_dict = get_timeslot_ids_dict(conn_fixture)
    timeslot_ids_in_events_ids_dict = [tup[3] for tup in events_ids_dict]
    temp_dict = {}
    for id in timeslot_ids_in_events_ids_dict:
        temp_dict[id] = True
    n_timeslots_in_events_dict = len(temp_dict.keys())

    try:
        assert all([x in timeslot_ids_in_events_ids_dict for x in timeslot_ids_dict.values()])
    except AssertionError:
        missing_timeslot_ids = [x for x in timeslot_ids_dict.values() if x not in timeslot_ids_in_events_ids_dict]
        reversed_timeslot_ids_dict = {value: key for key, value in timeslot_ids_dict.items()}
        missing_timeslot_records = [f"{k}: {v}" for k, v in reversed_timeslot_ids_dict.items() if k in missing_timeslot_ids]
        print(f"missing {len(missing_timeslot_ids)} out of {len(timeslot_ids_dict)} timeslot ids in the events_db. (only found {n_timeslots_in_events_dict})")
        print(f"missing these timeslot ids:\n{missing_timeslot_records}")
        assert all([x in timeslot_ids_in_events_ids_dict for x in timeslot_ids_dict.values()]), f"timeslots are missing from the events dimension table when min_start_datetime={min_datetime}"



