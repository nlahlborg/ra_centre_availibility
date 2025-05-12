"""
tests for functions in src/upload_utils.py
"""
#pylint: disable=import-error, wrong-import-position, line-too-long, redefined-outer-name
from datetime import datetime
import sys
from pathlib import Path
sys.path.insert(1, str(Path(__file__).parent.parent))
import pytest

from src.parser import DataValidationError
from src.upload import (
    get_list_of_unprocessed_object_names,
    generate_insert_sql, generate_insert_sql_batch,
    load_new_single_data, load_slot_events_batch,
    process_single_data,
    process_and_load_batch_data
)
from tests.helpers.helper_constants import (
    GET_LIST_OF_UNPROCESSED_OBJECT_NAMES_TEST_CONSTANT,
    GENERATE_INSERT_SQL_TEST_CONSTANT,
    GENERATE_INSERT_SQL_BATCH_TEST_CONSTANT,
    LOAD_NEW_SINGLE_DATA_TEST_CONSTANT,
    GET_FACILITIES_IDS_DICT_TEST_CONSTANT,
    GET_TIMESLOTS_IDS_DICT_TEST_CONSTANT,
    PROCESS_SINGLE_DATA_TEST_CONSTANT,
    LOAD_SLOT_EVENTS_BATCH_TEST_CONSTANT,
    PROCESS_AND_LOAD_BATCH_DATA_TEST_CONSTANT
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

#(data in, facility_id, timeslot_id, id out
@pytest.mark.parametrize("data_list,expected", LOAD_SLOT_EVENTS_BATCH_TEST_CONSTANT)
def test_load_slot_events_batch(conn_fixture, data_list, expected):
    """
    Test timeslot data load
    """
    cursor = conn_fixture.cursor()
    result = load_slot_events_batch(data_list, cursor)

    assert result == expected

@pytest.mark.parametrize("data,events_table_ids_dict,scraped_datetime,expected", PROCESS_SINGLE_DATA_TEST_CONSTANT)
def test_process_single_data(conn_fixture, data, events_table_ids_dict, scraped_datetime, expected):
    """
    test function that parses data and uploads any new data to facilities/timeslots table
    """
    # pylint: disable=too-many-arguments, too-many-positional-arguments
    facilities_ids_dict = GET_FACILITIES_IDS_DICT_TEST_CONSTANT
    timeslots_ids_dict = GET_TIMESLOTS_IDS_DICT_TEST_CONSTANT

    cursor = conn_fixture.cursor()
    try:
        result = process_single_data(
            data, 
            facilities_ids_dict,
            timeslots_ids_dict,
            events_table_ids_dict,
            scraped_datetime=scraped_datetime,
            inserted_datetime=datetime.now(),
            cursor=cursor
        )

        # don't compare scraped_datetime
        if result is not None:
            _ = result.pop("inserted_datetime")
            assert sorted(result.items()) == sorted(expected.items())
        else:
            assert result is None and expected is None
    except DataValidationError:
        # if a data validation error is detected check that this was expected
        assert expected == DataValidationError

@pytest.mark.parametrize("data,object_name,expected", PROCESS_AND_LOAD_BATCH_DATA_TEST_CONSTANT)
def test_process_and_load_batch_data(conn_fixture, data, object_name, expected):
    """
    test function that parses data and uploads any new data to facilities/timeslots table
    """
    result = process_and_load_batch_data(
        data=data,
        object_name=object_name,
        conn=conn_fixture,
        dry_run=False)
    
    assert result == expected