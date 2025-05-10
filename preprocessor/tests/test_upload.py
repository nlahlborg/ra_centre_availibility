"""
tests for functions in src/upload_utils.py
"""
#pylint: disable=import-error, wrong-import-position, line-too-long, redefined-outer-name
import sys
from pathlib import Path
sys.path.insert(1, str(Path(__file__).parent.parent))
import pytest

from src.upload import (
    get_list_of_unprocessed_object_names,
    generate_insert_sql, generate_insert_sql_batch, load_facility,
    load_timeslot, load_slot_events_batch
)
from tests.helpers.helper_constants import (
    GET_LIST_OF_UNPROCESSED_OBJECT_NAMES_TEST_CONSTANT,
    GENERATE_INSERT_SQL_TEST_CONSTANT,
    GENERATE_INSERT_SQL_BATCH_TEST_CONSTANT,
    LOAD_FACILITY_TEST_CONSTANT,
    LOAD_TIMESLOT_TEST_CONSTANT,
    SAMPLE_EVENTS_DATA
)

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

@pytest.mark.parametrize("data,id_col_name,table_name,expected_sql,expected_values", GENERATE_INSERT_SQL_TEST_CONSTANT)
def test_generate_insert_sql(data, id_col_name, table_name, expected_sql, expected_values):
    """
    Test sql insert generation
    """
    sql, values = generate_insert_sql(data, id_col_name, table_name)
    sql = sql.replace("    ", "")

    expected_sql = expected_sql.replace("    ", "")
    assert sql == expected_sql
    assert values == expected_values

@pytest.mark.parametrize("data_list,table_name,expected_sql,expected_values", GENERATE_INSERT_SQL_BATCH_TEST_CONSTANT)
def test_generate_insert_sql_batch(data_list, table_name, expected_sql, expected_values):
    """
    Test sql insert generation
    """
    sql, values = generate_insert_sql_batch(data_list, table_name)

    expected_sql = expected_sql.replace("    ", "").replace("\n", " ")
    assert sql.as_string() == expected_sql
    assert values == expected_values

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

def test_load_slot_events_batch(conn_fixture):
    """
    Test timeslot data load
    """
    data1 = SAMPLE_EVENTS_DATA.copy()
    data2 = SAMPLE_EVENTS_DATA.copy()
    data2["num_people"] = 0
    data_list = [data1, data2]
    cursor = conn_fixture.cursor()
    result = load_slot_events_batch(data_list, cursor)

    assert result

# def test_load_slot_events_batch_stale_scraped_datetime(conn_fixture):
#     """
#     Test timeslot data load
#     """
#     cursor = conn_fixture.cursor()

#     data = {
#         'num_people': 1,
#         'scraped_datetime': datetime.datetime(2024, 4, 22, 1, 1, tzinfo=RA_CENTRE_TZ),
#         'week_number': 6,
#         'facility_id': 1,
#         'timeslot_id': 1
#         }

#     try:
#         _ = load_slot_events_batch(data, cursor)
#         value_error_raised = False
#     except ValueError:
#         value_error_raised = True

#     assert value_error_raised
