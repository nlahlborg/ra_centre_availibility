"""
short simple unit test fixtures
"""
#pylint: disable=import-error, wrong-import-position, line-too-long
import sys
from pathlib import Path
sys.path.insert(1, str(Path(__file__).parent.parent.parent))
import datetime
from src.setup import RA_CENTRE_TZ

SAMPLE_RAW_JSON = {
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
}

SAMPLE_PARSED_DATA = {
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

SAMPLE_RESTRUCTURED_DATA = {
    'facilities': {
        'facility_name': 'Badminton Court 1',
        'facility_type': 'badminton_court'
        },
    'reservation_system_events': {
        'num_people': 1,
        'scraped_datetime': datetime.datetime(2025, 4, 26, 7, 2, tzinfo=RA_CENTRE_TZ),
        'week_number': 6
        },
    'timeslots': {
        'day_of_week': 'Friday',
        'end_time': datetime.time(13, 0, tzinfo=RA_CENTRE_TZ),
        'release_interval_days': 7,
        'start_time': datetime.time(12, 0, tzinfo=RA_CENTRE_TZ)
        }
}

COLUMN_MAP = {
    'day_of_week': 'timeslots',
    'end_time': 'timeslots',
    'facility_id': 'reservation_system_events',
    'facility_name': 'facilities',
    'facility_type': 'facilities',
    'inserted_datetime': 'reservation_system_events',
    'num_people': 'reservation_system_events',
    'release_interval_days': 'timeslots',
    'scraped_datetime': 'reservation_system_events',
    'start_time': 'timeslots',
    'timeslot_id': 'reservation_system_events',
    'week_number': 'reservation_system_events'
    }

GET_FACILITY_TYPE_TEST_CONSTANT = (
    ("Squash Court 5", "squash_court"),
    ("Archery Range Lane 1", "archery_range_lane"),
    ("Pickleball Centre", "pickleball_centre"),
    ("Photo Studio", "photo_studio")
)

PARSE_OBJECT_NAME_TEST_CONSTANT = (
    (
        "raw_centre_raw_20250426T000200Z.json", 
        "raw_centre_raw_", 
        datetime.datetime(2025, 4, 26, 0, 2, tzinfo=RA_CENTRE_TZ)
    ),
)

PARSE_DATA_TEST_CONSTANT = (
    (
        SAMPLE_RAW_JSON,
        datetime.datetime(2025, 4, 26, 7, 2, tzinfo=RA_CENTRE_TZ),
        SAMPLE_PARSED_DATA
    ),
)

# (object_names_in, filepath, expected)
GET_LIST_OF_UNPROCESSED_OBJECT_NAMES_TEST_CONSTANT = (
    #nothing
    ([], []),
    #some unprocessed
    (
        [
            "raw_centre_raw_20250426T000200Z.json",
            "raw_centre_raw_20250426T000433Z.json",
            "raw_centre_raw_20250428T000000Z.json",
        ],
        [
            "raw_centre_raw_20250428T000000Z.json"
        ]
    ),
    #none_processed
    (
        [
            "raw_centre_raw_20250428T000000Z.json",
            "raw_centre_raw_20250428T000100Z.json",
        ],
        [
            "raw_centre_raw_20250428T000000Z.json",
            "raw_centre_raw_20250428T000100Z.json",
        ]
    ),
    #all_processed
    (
        [
            "raw_centre_raw_20250426T000200Z.json",
            "raw_centre_raw_20250426T000433Z.json",
        ],
        []
    ),
    #unprocessed but stale date
    (
        [
            "raw_centre_raw_20240426T000200Z.json",
        ],
        []
    ),
)

RESTRUCTURE_DATA_FOR_TABLES_TEST_CONSTANT = (
    (SAMPLE_PARSED_DATA, SAMPLE_RESTRUCTURED_DATA),
)

#data, id_col_name, table_name, expected_sql, expected_values
GENERATE_INSERT_SQL_TEST_CONSTANT = (
    (
        SAMPLE_RESTRUCTURED_DATA["facilities"],
        "facility_id",
        "facilities",
        """
            INSERT INTO source.facilities (facility_name, facility_type)
            VALUES (%s, %s)
            RETURNING facility_id
        """,
        ('Badminton Court 1', 'badminton_court')
    ),
    (
        SAMPLE_RESTRUCTURED_DATA["timeslots"],
        "timeslot_id",
        "timeslots",
        """
            INSERT INTO source.timeslots (day_of_week, end_time, release_interval_days, start_time)
            VALUES (%s, %s, %s, %s)
            RETURNING timeslot_id
        """,
        ('Friday', datetime.time(13, 0, tzinfo=RA_CENTRE_TZ), 7, datetime.time(12, 0, tzinfo=RA_CENTRE_TZ))
    ),
    (
        SAMPLE_RESTRUCTURED_DATA["reservation_system_events"],
        "event_id",
        "reservation_system_events",
        """
            INSERT INTO source.reservation_system_events (num_people, scraped_datetime, week_number)
            VALUES (%s, %s, %s)
            RETURNING event_id
        """,
        (1, datetime.datetime(2025, 4, 26, 7, 2, tzinfo=RA_CENTRE_TZ), 6)
    ),
)

#(data in, id out)
LOAD_FACILITY_TEST_CONSTANT = (
    #facility already matches existing id = 1
    (
        {
            'facility_name': 'Badminton Court 1',
            'facility_type': 'badminton_court'
        },
        1
    ),
    #facility doesn't match existing id

    (
        {
            'facility_name': 'other facility',
            'facility_type': 'other_facility'
        },
        2
    ),
)

#(data in, id out)
LOAD_TIMESLOT_TEST_CONSTANT = (
    #timeslot already matches existing id = 1
    (
        {
        'day_of_week': 'Friday',
        'end_time': datetime.time(13, 0, tzinfo=RA_CENTRE_TZ),
        'release_interval_days': 7,
        'start_time': datetime.time(12, 00, tzinfo=RA_CENTRE_TZ)
        },
        1
    ),
    #timeslot doesn't match existing id

    (
        {
        'day_of_week': 'Saturday',
        'end_time': datetime.time(13, 0, tzinfo=RA_CENTRE_TZ),
        'release_interval_days': 7,
        'start_time': datetime.time(12, 0, tzinfo=RA_CENTRE_TZ)
        },
        2
    ),
)

#(data in, facility_id, timeslot_id, id out)
LOAD_SLOT_EVENT_TEST_CONSTANT = (
    #slot event exactly matches existing record, with scraped_datetime greater than previous
    (
       {
        'num_people': 1,
        'scraped_datetime': datetime.datetime(2026, 4, 22, 1, 1, tzinfo=RA_CENTRE_TZ),
        'week_number': 6
        },
        1,
        1,
        1
    ),
    #slot event exactly matches existing record except num_people, with scraped_datetime greater than previous
    (
       {
        'num_people': 0,
        'scraped_datetime': datetime.datetime(2026, 4, 22, 1, 1, tzinfo=RA_CENTRE_TZ),
        'week_number': 6
        },
        1,
        1,
        2
    ),
    #slot event is for a timeslot_id that is new but otherwise the same
    (
       {
        'num_people': 1,
        'scraped_datetime': datetime.datetime(2026, 4, 22, 1, 1, tzinfo=RA_CENTRE_TZ),
        'week_number': 6
        },
        1,
        2,
        2
    ),
    #slot event is for a week that is new but otherwise the same
    (
       {
        'num_people': 1,
        'scraped_datetime': datetime.datetime(2026, 4, 22, 1, 1, tzinfo=RA_CENTRE_TZ),
        'week_number': 7
        },
        1,
        1,
        2
    )
)
