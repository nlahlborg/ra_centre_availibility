import sys
import pytest
from pathlib import Path
sys.path.insert(1, str(Path(__file__).parent.parent))

from src.parser import get_slot_id, get_facility_type
from data_constants import RESPONSE_DATA_SAMPLE, EXPECTED_FACILITY_NAMES, EXPECTED_SLOT_IDS

@pytest.mark.parametrize("row,expected", list(zip(RESPONSE_DATA_SAMPLE, EXPECTED_SLOT_IDS)))
def test_get_slot_id(row, expected):
    slot_id = get_slot_id(row)
    assert slot_id == expected

@pytest.mark.parametrize("row,expected", list(zip(RESPONSE_DATA_SAMPLE, EXPECTED_FACILITY_NAMES)))
def test_get_facility_type(row, expected):
    facility_type = get_facility_type(row)
    assert facility_type == expected