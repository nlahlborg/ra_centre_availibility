"""
tests for functions in src/parser_utils.py
"""
#pylint: disable=import-error, wrong-import-position, line-too-long
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.web_query import get_context_auth
from web_scraper.tests.fixture_constants import HTML_PAYLOAD_SAMPLE

def test_get_context_auth():
    """
    unit test the regex from the get_context_auth function
    """
    html = HTML_PAYLOAD_SAMPLE
    action = "ts_avo.AvocadoSiteController"

    result = get_context_auth(html)

    assert result["actions"][action]["ms"][0]["name"] == "dispatch"
    assert result["actions"][action]["ms"][0]["csrf"] == "VmpFPSxNakF5TlMwd05TMHdNMVF3TXpvMU5qbzBNaTQyTmpWYSxGMFJFNXFzY1E2eFpXN1hDMkswVzlZNkJueWozS2dRMkxwMHYxR1ZjM0VvPSxNMkUyTm1FNQ=="
    assert result["actions"][action]["ms"][0]["ns"] == "ts_avo"
    assert int(result["actions"][action]["ms"][0]["ver"]) == 43
    assert result["vf"]["vid"] == "0664x00000AprDY"
    assert result["service"] == "apexremote"

if __name__ == "__main__":
    pass
