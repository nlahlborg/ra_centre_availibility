"""
tests for functions in src/upload_utils.py
"""
#pylint: disable=import-error, wrong-import-position, line-too-long, redefined-outer-name
from datetime import datetime
import sys
from pathlib import Path
sys.path.insert(1, str(Path(__file__).parent.parent))

from src.download import (
    get_sql_facilities_table, get_sql_registration_system_events_table,
    get_sql_timeslots_table, get_facilities_ids_dict,
    get_timeslots_ids_dict, get_registration_system_events_ids_dict
)
from tests.helpers.helper_constants import (
    SAMPLE_FACILITIES_DATA, SAMPLE_TIMESLOTS_DATA, SAMPLE_EVENTS_DATA,
    GET_FACILITIES_IDS_DICT_TEST_CONSTANT, GET_TIMESLOTS_IDS_DICT_TEST_CONSTANT,
    GET_REGISTRATION_SYSTEM_EVENTS_IDS_DICT_TEST_CONSTANT
)

def test_get_sql_facilities_table(conn_fixture) -> None:
    """
    Test get_list_of_unprocessed_object_names
    """
    result = get_sql_facilities_table(conn_fixture)
    expected = [tuple([1] + list(SAMPLE_FACILITIES_DATA.values()))]

    assert result == expected

def test_get_sql_timeslots_table(conn_fixture) -> None:
    """
    Test get_list_of_unprocessed_object_names
    """
    result = get_sql_timeslots_table(conn_fixture)
    expected = [tuple([1] + list(SAMPLE_TIMESLOTS_DATA.values()))]

    assert result == expected

def test_get_sql_registration_system_events_table_base(conn_fixture) -> None:
    """
    Test get_list_of_unprocessed_object_names
    """
    result = get_sql_registration_system_events_table(conn_fixture)
    sample_data = SAMPLE_EVENTS_DATA.copy()
    _ = sample_data.pop("scraped_datetime")
    sample_data["facility_id"] = 1
    sample_data["timeslot_id"] = 1
    expected = [tuple([1] + list(sample_data.values()))]

    assert result == expected

def test_get_sql_registration_system_events_table_stale_starttimes(conn_fixture) -> None:
    """
    Test get_list_of_unprocessed_object_names
    """
    result = get_sql_registration_system_events_table(
        conn=conn_fixture,
        min_start_datetime=datetime.now() #just something newer than the sample data
        )
    expected = []

    assert result == expected

def test_get_facilities_ids_dict(conn_fixture):
    """
    test list comprehension of facilities table
    """
    result = get_facilities_ids_dict(conn_fixture)
    expected = GET_FACILITIES_IDS_DICT_TEST_CONSTANT

    assert result == expected

def test_get_timeslots_ids_dict(conn_fixture):
    """
    test list comprehension of facilities table
    """
    result = get_timeslots_ids_dict(conn_fixture)
    expected = GET_TIMESLOTS_IDS_DICT_TEST_CONSTANT

    assert result == expected

def test_get_registration_system_events_ids_dict(conn_fixture):
    """
    test list comprehension of facilities table
    """
    result = get_registration_system_events_ids_dict(conn_fixture)
    expected = GET_REGISTRATION_SYSTEM_EVENTS_IDS_DICT_TEST_CONSTANT

    assert result == expected
