"""
short simple unit test fixtures
"""
#pylint: disable=import-error, wrong-import-position, line-too-long
import sys
from pathlib import Path
sys.path.insert(1, str(Path(__file__).parent.parent.parent))
import datetime
from src.setup import RA_CENTRE_TZ

GET_FACILITY_TYPE_FIXTURE = (
    ("Squash Court 5", "squash_court"),
    ("Archery Range Lane 1", "archery_range_lane"),
    ("Pickleball Centre", "pickleball_centre"),
    ("Photo Studio", "photo_studio")
)

PARSE_OBJECT_NAME_FIXTURE = (
    ("raw_centre_raw_20250426T000200Z.json", "raw_centre_raw_", datetime.datetime(2025, 4, 26, 7, 2, tzinfo=RA_CENTRE_TZ)),
)

PARSE_DATA_FIXTURE = (
    (
        {
            "ageMaxInYears": 120,
            "ageMinInYears": 18,
            "barcode": "389937",
            "code": "INST-389937",
            "divisionCode": "DIV-002",
            "endDate": 1738886400000,
            "facilityName": "Badminton Court 1",
            "hasRegEarlyStarted": True,
            "hasRegEnded": False,
            "hasRegPriorityStarted": True,
            "hasRegReturnStarted": True,
            "hasRegStarted": True,
            "instanceType": "Requires_Registration",
            "isLite": True,
            "isPackage": False,
            "locationCode": "LOC-000002",
            "locationName": "The RA Centre",
            "makeupClassesEnabled": False,
            "marketingDescription": "Non Prime bookings are Monday - Friday from 7:00am - 4:00pm. One hour “court rental” is open to the GENERAL PUBLIC, RA Badminton Club Members and RA members for a fee. Juniors (12 to 17 years) are welcome (and may book a court) but must be accompanied by an adult 18+.",
            "maxAge": 120,
            "maxPeople": 1,
            "minAge": 18,
            "name": "Badminton Court 1 - Friday  Feb 07 - 3:00 PM",
            "numPeople": 1,
            "numWaitlist": 0,
            "programCode": "PROG-000317",
            "regCancel": 1738785600000,
            "regEarly": 1738332000000,
            "regEnd": 1738960200000,
            "regPriority": 1738332000000,
            "regReturn": 1738332000000,
            "regStart": 1738332000000,
            "schedule": [
                {
                    "description": "",
                    "endDatetime": 1738962000000,
                    "isRecurrence": False,
                    "startDatetime": 1738958400000,
                    "subject": "Badminton Court 1 - Friday  Feb 07 - 3:00 PM"
                }
            ],
            "startDate": 1738958400000,
            "tracksAttendance": False,
            "weekDays": [
                "Fri"
            ]
        },
        datetime.datetime(2025, 4, 26, 7, 2, tzinfo=RA_CENTRE_TZ),
        {
            'day_of_week': 'Friday',
            'end_time': datetime.time(13, 0, tzinfo=RA_CENTRE_TZ),
            'facility_name': 'Badminton Court 1',
            'facility_type': 'badminton_court',
            'num_people': 1,
            'release_interval_days': 7,
            'scraped_datetime': datetime.datetime(2025, 4, 26, 7, 2, tzinfo=RA_CENTRE_TZ),
            'start_time': datetime.time(12, 0, tzinfo=RA_CENTRE_TZ),
            'week_number': 6
        }
    ),
)