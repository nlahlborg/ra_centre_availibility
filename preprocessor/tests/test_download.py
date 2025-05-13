"""
tests for functions in src/upload_utils.py
"""
#pylint: disable=import-error, wrong-import-position, line-too-long, redefined-outer-name
from datetime import datetime
import sys
from pathlib import Path
sys.path.insert(1, str(Path(__file__).parent.parent))
import pytest

from tests.common import clear_starter_data
from src.download import (
    get_sql_facilities_table, get_sql_reservation_system_events_table,
    get_sql_timeslots_table, get_facility_ids_dict,
    get_timeslot_ids_dict, get_reservation_system_events_ids_dict
)
from tests.helpers.helper_constants import (
    SAMPLE_FACILITIES_DATA, SAMPLE_TIMESLOTS_DATA, SAMPLE_EVENTS_DATA,
    GET_SQL_RESERVATION_SYSTEM_EVENTS_TABLE_TEST_CONSTANT,
    GET_facility_ids_dict_TEST_CONSTANT, get_timeslot_ids_dict_TEST_CONSTANT,
    GET_RESERVATION_SYSTEM_EVENTS_IDS_DICT_TEST_CONSTANT,
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

@pytest.mark.parametrize("min_start_datetime,expected", GET_SQL_RESERVATION_SYSTEM_EVENTS_TABLE_TEST_CONSTANT)
def test_get_sql_reservation_system_events_table_base(conn_fixture, min_start_datetime, expected) -> None:
    """
    Test get_list_of_unprocessed_object_names
    """
    result = get_sql_reservation_system_events_table(conn_fixture, min_start_datetime)

    assert result == expected

def test_get_facility_ids_dict(conn_fixture):
    """
    test list comprehension of facilities table
    """
    result = get_facility_ids_dict(conn_fixture)
    expected = GET_facility_ids_dict_TEST_CONSTANT

    assert result == expected

def test_get_timeslot_ids_dict(conn_fixture):
    """
    test list comprehension of facilities table
    """
    result = get_timeslot_ids_dict(conn_fixture)
    expected = get_timeslot_ids_dict_TEST_CONSTANT

    assert result == expected

def test_get_reservation_system_events_ids_dict(conn_fixture):
    """
    test list comprehension of facilities table
    """
    result = get_reservation_system_events_ids_dict(conn_fixture)
    expected = GET_RESERVATION_SYSTEM_EVENTS_IDS_DICT_TEST_CONSTANT

    assert result == expected

def test_table_gets_cleared(conn_fixture):
    cursor = conn_fixture.cursor()
    clear_starter_data(cursor)
    cursor.close()
    conn_fixture.commit()

    assert get_facility_ids_dict(conn_fixture) == {}
    assert get_timeslot_ids_dict(conn_fixture) == {}
    assert get_reservation_system_events_ids_dict(conn_fixture) == {}
