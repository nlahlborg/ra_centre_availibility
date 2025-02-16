import sys
from pathlib import Path
sys.path.insert(1, str(Path(__file__).parent.parent.parent))

from web_scraper.src.upload import compare_data
from data_constants import EXISTING_DB_DATA, NEW_DB_DATA, CHANGED_DB_DATA

def test_compare_data_same_data():
    data1 = EXISTING_DB_DATA.copy()
    data2 = data1.copy()

    result = compare_data(data1, data2)

    assert not result, "expected compare to return an emtpy result for identical input data"

def test_compare_data_new_data():
    data1 = EXISTING_DB_DATA.copy()
    data2 = NEW_DB_DATA.copy()

    result = compare_data(data1, data2)

    assert len(result) == len(data2), "expected to return object with same number of rows as new data"

def test_compare_data_changed_data():
    data1 = EXISTING_DB_DATA.copy()
    data2 = CHANGED_DB_DATA.copy()

    result = compare_data(data1, data2)

    assert len(result) == 1, "expected to return object with only hte changed data"