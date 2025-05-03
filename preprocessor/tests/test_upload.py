"""
tests for functions in src/upload_utils.py
"""
#pylint: disable=import-error, wrong-import-position, line-too-long, redefined-outer-name
import sys
import os
import datetime
from pathlib import Path
sys.path.insert(1, str(Path(__file__).parent.parent))
import pytest
from pytest_postgresql import factories

from src.setup import RA_CENTRE_TZ
from src.upload import (
    get_list_of_unprocessed_object_names,
    get_table_column_mapping, restructure_data_for_tables,
    generate_insert_sql, load_facility,
    load_timeslot, load_slot_event
)
from tests.helpers.helper_constants import (
    GET_LIST_OF_UNPROCESSED_OBJECT_NAMES_TEST_CONSTANT,
    COLUMN_MAP,
    RESTRUCTURE_DATA_FOR_TABLES_TEST_CONSTANT,
    GENERATE_INSERT_SQL_TEST_CONSTANT,
    LOAD_FACILITY_TEST_CONSTANT,
    LOAD_TIMESLOT_TEST_CONSTANT,
    LOAD_SLOT_EVENT_TEST_CONSTANT
)

postgresql_local_dev = factories.postgresql_noproc(
    user='postgres',
    password='postgres',
    load=[
        Path(__file__).parent / "helpers" / "helper_helper_loaded_objects.sql",
        Path(__file__).parent / "helpers" / "helper_helper_loaded_objects_blank.sql",
        Path(__file__).parent / "helpers" / "source_facilities.sql",
        Path(__file__).parent / "helpers" / "source_timeslots.sql",
        Path(__file__).parent / "helpers" / "source_reservation_system_events.sql"
        ])
conn_fixture = factories.postgresql("postgresql_local_dev", dbname="test")

@pytest.mark.parametrize("object_names,expected", GET_LIST_OF_UNPROCESSED_OBJECT_NAMES_TEST_CONSTANT)
def test_get_list_of_unprocessed_object_names(conn_fixture, object_names, expected) -> None:
    """
    Test get_list_of_unprocessed_object_names
    """
    result = get_list_of_unprocessed_object_names(object_names, conn_fixture)
    try:
        assert result == expected
    except AssertionError as e:
        conn_fixture.close()
        raise e@pytest.mark.parametrize("object_names,expected", GET_LIST_OF_UNPROCESSED_OBJECT_NAMES_TEST_CONSTANT)

def test_get_list_of_unprocessed_object_names_blank_table(conn_fixture) -> None:
    """
    Test get_list_of_unprocessed_object_names
    """

    object_names = ["raw_centre_raw_20250426T000200Z.json"]
    expected = object_names.copy()
    result = get_list_of_unprocessed_object_names(object_names, conn_fixture, table="helper_loaded_objects_blank")
    try:
        assert result == expected
    except AssertionError as e:
        conn_fixture.close()
        raise e

def test_get_table_column_mapping(conn_fixture):
    """
    Test that column mapper matches expectation
    """
    result = get_table_column_mapping(conn_fixture)
    try:
        assert result == COLUMN_MAP
    except AssertionError as e:
        conn_fixture.close()
        raise e

@pytest.mark.parametrize("data,expected", RESTRUCTURE_DATA_FOR_TABLES_TEST_CONSTANT)
def test_restructure_data_for_tables(data, expected):
    """
    Test function that sorts data into columns
    """
    result = restructure_data_for_tables(data, COLUMN_MAP)
    try:
        assert result == expected
    except AssertionError as e:
        conn_fixture.close()
        raise e

@pytest.mark.parametrize("data,id_col_name,table_name,expected_sql,expected_values", GENERATE_INSERT_SQL_TEST_CONSTANT)
def test_generate_insert_sql(data, id_col_name, table_name, expected_sql, expected_values):
    """
    Test sql insert generation
    """
    sql, values = generate_insert_sql(data, id_col_name, table_name)
    sql = sql.replace("    ", "")

    expected_sql = expected_sql.replace("    ", "")
    try:
        assert sql == expected_sql
        assert values == expected_values
    except AssertionError as e:
        conn_fixture.close()
        raise e

@pytest.mark.parametrize("data,expected", LOAD_FACILITY_TEST_CONSTANT)
def test_load_facility(conn_fixture, data, expected):
    """
    Test facility data load
    """
    cursor = conn_fixture.cursor()
    result = load_facility(data, cursor)

    try:
        assert result == expected
    except AssertionError as e:
        conn_fixture.close()
        raise e

@pytest.mark.parametrize("data,expected", LOAD_TIMESLOT_TEST_CONSTANT)
def test_load_timeslot(conn_fixture, data, expected):
    """
    Test timeslot data load
    """
    cursor = conn_fixture.cursor()
    result = load_timeslot(data, cursor)

    try:
        assert result == expected
    except AssertionError as e:
        conn_fixture.close()
        raise e

@pytest.mark.parametrize("data,facility_id,timeslot_id,expected", LOAD_SLOT_EVENT_TEST_CONSTANT)
def test_load_slot_event(conn_fixture, data, facility_id, timeslot_id, expected):
    """
    Test timeslot data load
    """
    cursor = conn_fixture.cursor()
    result = load_slot_event(data, facility_id, timeslot_id, cursor)

    try:
        assert result == expected
    except AssertionError as e:
        conn_fixture.close()
        raise e

def test_load_slot_event_stale_scraped_datetime(conn_fixture):
    """
    Test timeslot data load
    """
    cursor = conn_fixture.cursor()

    data = {
        'num_people': 1,
        'scraped_datetime': datetime.datetime(2024, 4, 22, 1, 1, tzinfo=RA_CENTRE_TZ),
        'week_number': 6
        }
    facility_id = 1
    timeslot_id = 1

    try:
        _ = load_slot_event(data, facility_id, timeslot_id, cursor)
        value_error_raised = False
    except ValueError:
        value_error_raised = True

    assert value_error_raised
