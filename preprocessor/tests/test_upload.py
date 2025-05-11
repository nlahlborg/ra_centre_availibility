"""
tests for functions in src/upload_utils.py
"""
#pylint: disable=import-error, wrong-import-position, line-too-long, redefined-outer-name
from datetime import datetime
import sys
from pathlib import Path
sys.path.insert(1, str(Path(__file__).parent.parent))
import pytest

from src.upload import (
    get_list_of_unprocessed_object_names,
    generate_insert_sql, generate_insert_sql_batch,
    load_new_single_data, load_slot_events_batch,
    process_single_data
)
from src.download import (
    get_facilities_ids_dict,
    get_timeslots_ids_dict,
    get_reservation_system_events_ids_dict
)
from tests.helpers.helper_constants import (
    GET_LIST_OF_UNPROCESSED_OBJECT_NAMES_TEST_CONSTANT,
    GENERATE_INSERT_SQL_TEST_CONSTANT,
    GENERATE_INSERT_SQL_BATCH_TEST_CONSTANT,
    LOAD_NEW_SINGLE_DATA_TEST_CONSTANT,
    SAMPLE_EVENTS_DATA,
    PROCESS_SINGLE_DATA_TEST_CONSTANT
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

@pytest.mark.parametrize("data,ids_dict,table_name,id_col_name,schema,expected", LOAD_NEW_SINGLE_DATA_TEST_CONSTANT)
def test_load_new_single_data(conn_fixture, data, ids_dict, table_name, id_col_name, schema, expected):
    """
    Test facility data load
    """
    # pylint: disable=too-many-arguments, too-many-positional-arguments
    cursor = conn_fixture.cursor()
    result = load_new_single_data(
        data=data,
        ids_dict=ids_dict,
        table_name=table_name,
        id_col_name=id_col_name,
        schema=schema,
        cursor=cursor
    )

    assert result == expected

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

@pytest.mark.parametrize("data,expected", PROCESS_SINGLE_DATA_TEST_CONSTANT)
def test_process_single_data(conn_fixture, data, expected):
    # pylint: disable=too-many-arguments, too-many-positional-arguments
    facilities_ids_dict = get_facilities_ids_dict(conn_fixture)
    timeslots_ids_dict = get_timeslots_ids_dict(conn_fixture)
    events_table_ids_dict = get_reservation_system_events_ids_dict(conn_fixture)

    cursor = conn_fixture.cursor()
    result = process_single_data(
        data, 
        facilities_ids_dict,
        timeslots_ids_dict,
        events_table_ids_dict,
        scraped_datetime=datetime.now(),
        inserted_datetime=datetime.now(),
        cursor=cursor
    )

    # don't compare scraped_datetime
    if result is not None:
        _ = result.pop("scraped_datetime")
        _ = result.pop("inserted_datetime")
        assert sorted(result) == sorted(expected)
    else:
        assert result is None and expected is None