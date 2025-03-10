"""
tests for functions in src/parser_utils.py
"""
#pylint: disable=import-error, wrong-import-position
import sys
from pathlib import Path
import pytest
sys.path.insert(1, str(Path(__file__).parent.parent))

from tests.data_constants import RESPONSE_DATA_SAMPLE, EXPECTED_FACILITY_NAMES, EXPECTED_SLOT_IDS
from src.parser import get_slot_id, get_facility_type

@pytest.mark.parametrize("row,expected", list(zip(RESPONSE_DATA_SAMPLE, EXPECTED_SLOT_IDS)))
def test_get_slot_id(row, expected):
    """
    Test the get_slot_id function.
    """
    slot_id = get_slot_id(row)
    assert slot_id == expected

@pytest.mark.parametrize("row,expected", list(zip(RESPONSE_DATA_SAMPLE, EXPECTED_FACILITY_NAMES)))
def test_get_facility_type(row, expected):
    """
    Test the get facility type function
    """
    facility_type = get_facility_type(row)
    assert facility_type == expected
