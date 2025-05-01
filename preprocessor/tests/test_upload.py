"""
tests for functions in src/upload_utils.py
"""
#pylint: disable=import-error, wrong-import-position
import sys
from pathlib import Path
sys.path.insert(1, str(Path(__file__).parent.parent))
import pytest
from pytest_postgresql import factories

from src.upload import get_list_of_unprocessed_object_names
from tests.helpers.helper_constants import GET_LIST_OF_UNPROCESSED_OBJECT_NAMES_FIXTURE

fixture_file_path = Path(__file__).parent / "helpers\helper_helper_loaded_objects.sql"
postgresql_local_dev = factories.postgresql_noproc(user='postgres', password='postgres', load=[fixture_file_path])
conn_fixture = factories.postgresql("postgresql_local_dev", dbname="test")

@pytest.mark.parametrize("object_names,expected", GET_LIST_OF_UNPROCESSED_OBJECT_NAMES_FIXTURE)
def test_get_list_of_unprocessed_object_names(conn_fixture, object_names, expected) -> None:
    """
    Test get_list_of_unprocessed_object_names
    """
    print("started test_get_...")

    result = get_list_of_unprocessed_object_names(object_names, conn_fixture)
    assert result == expected
    conn_fixture.close()

if __name__ == "__main__":
    test_get_list_of_unprocessed_object_names()