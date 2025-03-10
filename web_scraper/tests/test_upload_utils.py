"""
tests for functions in src/upload_utils.py
"""
#pylint: disable=import-error, wrong-import-position
import sys
from pathlib import Path
sys.path.insert(1, str(Path(__file__).parent.parent))

from tests.data_constants import EXISTING_DB_DATA, NEW_DB_DATA, CHANGED_DB_DATA
from src.upload import compare_data

def test_compare_data_same_data():
    """
    test the compare_data function for the case where the data is the same
    """
    data1 = EXISTING_DB_DATA.copy()
    data2 = data1.copy()

    result = compare_data(data1, data2)

    assert not result, "expected compare to return an emtpy result for identical input data"

def test_compare_data_new_data():
    """
    test the compare_data function for the case where there are new reservation
    slots released
    """
    data1 = EXISTING_DB_DATA.copy()
    data2 = NEW_DB_DATA.copy()

    result = compare_data(data1, data2)

    assert len(result) == len(data2), \
        "expected to return object with same number of rows as new data"

def test_compare_data_changed_data():
    """
    test the compare_data function for the case where there are updates to 
    existing reservation slots
    """
    data1 = EXISTING_DB_DATA.copy()
    data2 = CHANGED_DB_DATA.copy()

    result = compare_data(data1, data2)

    assert len(result) == 1, \
        "expected to return object with only the changed data"
