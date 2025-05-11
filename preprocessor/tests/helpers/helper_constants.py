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
    'end_time': datetime.time(21, 0, tzinfo=RA_CENTRE_TZ),
    'facility_name': 'Badminton Court 1',
    'facility_type': 'badminton_court',
    'num_people': 1,
    'release_interval_days': 7,
    'scraped_datetime': datetime.datetime(2025, 4, 26, 7, 2, tzinfo=RA_CENTRE_TZ),
    'start_time': datetime.time(20, 0, tzinfo=RA_CENTRE_TZ),
    'week_number': 6
}

SAMPLE_FACILITIES_DATA = {
    'facility_name': 'Badminton Court 1',
    'facility_type': 'badminton_court'
}

SAMPLE_TIMESLOTS_DATA = {
    'start_time': datetime.time(20, 0, tzinfo=RA_CENTRE_TZ),
    'end_time': datetime.time(21, 0, tzinfo=RA_CENTRE_TZ),
    'day_of_week': 'Friday',
    'release_interval_days': 7
}

SAMPLE_EVENTS_DATA = {
    'num_people': 1,
    'scraped_datetime': datetime.datetime(2025, 4, 26, 7, 2, tzinfo=RA_CENTRE_TZ),
    'week_number': 6,
}

#min start_datetime, expected
GET_SQL_RESERVATION_SYSTEM_EVENTS_TABLE_TEST_CONSTANT = (
    #no start time provided
    (
        None,
        [
            (2, 1, 6, 1, 1),
            (3, 0, 7, 1, 1),
        ]
    ),
    #all start times in db are stale
    (
        datetime.datetime.now(),
        []
    ),
)

GET_FACILITIES_IDS_DICT_TEST_CONSTANT = {
    ('Badminton Court 1', 'badminton_court'): 1
}

GET_TIMESLOTS_IDS_DICT_TEST_CONSTANT = {
    (datetime.time(20, 0, tzinfo=RA_CENTRE_TZ), datetime.time(21, 0, tzinfo=RA_CENTRE_TZ), 'Friday',  7): 1
}

GET_RESERVATION_SYSTEM_EVENTS_IDS_DICT_TEST_CONSTANT = {
    (1, 6, 1, 1): 2,
    (0, 7, 1, 1): 3
}

GET_FACILITY_TYPE_TEST_CONSTANT = (
    ("Squash Court 5", "squash_court"),
    ("Archery Range Lane 1", "archery_range_lane"),
    ("Pickleball Centre", "pickleball_centre"),
    ("Photo Studio", "photo_studio")
)

PARSE_OBJECT_NAME_TEST_CONSTANT = (
    #no daylight savings
    (
        "raw_centre_raw_20250126T000200Z.json", 
        "raw_centre_raw_", 
        datetime.datetime(2025, 1, 26, 0, 2, 0, tzinfo=RA_CENTRE_TZ)
    ),
    #yes daylight savings
    (
        "raw_centre_raw_20250502T020513Z.json", 
        "raw_centre_raw_", 
        datetime.datetime(2025, 5, 2, 2, 5, 13, tzinfo=RA_CENTRE_TZ)
    )
)

PARSE_DATA_TEST_CONSTANT = (
    (
        SAMPLE_RAW_JSON,
        datetime.datetime(2025, 4, 26, 7, 2, tzinfo=RA_CENTRE_TZ),
        SAMPLE_FACILITIES_DATA,
        SAMPLE_TIMESLOTS_DATA,
        SAMPLE_EVENTS_DATA
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

#data, id_col_name, table_name, expected_sql, expected_values
GENERATE_INSERT_SQL_TEST_CONSTANT = (
    (
        SAMPLE_FACILITIES_DATA,
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
        SAMPLE_TIMESLOTS_DATA,
        "timeslot_id",
        "timeslots",
        """
            INSERT INTO source.timeslots (start_time, end_time, day_of_week, release_interval_days)
            VALUES (%s, %s, %s, %s)
            RETURNING timeslot_id
        """,
        (datetime.time(20, 0, tzinfo=RA_CENTRE_TZ), datetime.time(21, 0, tzinfo=RA_CENTRE_TZ), 'Friday', 7)
    )
)

GENERATE_INSERT_SQL_BATCH_TEST_CONSTANT = (
    (
        [SAMPLE_EVENTS_DATA.copy(), SAMPLE_EVENTS_DATA.copy()],
        "reservation_system_events",
        '''INSERT INTO "source"."reservation_system_events" ("num_people", "scraped_datetime", "week_number")
            VALUES (%s, %s, %s)''',
        [
            (1, datetime.datetime(2025, 4, 26, 7, 2, tzinfo=RA_CENTRE_TZ), 6),
            (1, datetime.datetime(2025, 4, 26, 7, 2, tzinfo=RA_CENTRE_TZ), 6)
        ]
    ),
)

#data,ids_dict,table_name,id_col_name,schema,expected_id)
LOAD_NEW_SINGLE_DATA_TEST_CONSTANT = (
    #facility already matches existing id = 1
    (
        {
            'facility_name': 'Badminton Court 1',
            'facility_type': 'badminton_court'
        },
        {('Badminton Court 1', 'badminton_court'): 1},
        "facilities",
        "facility_id",
        "source",
        1
    ),
    #facility doesn't matches existing id = 1
    (
        {
            'facility_name': 'Other Court 1',
            'facility_type': 'other_court'
        },
        {('Badminton Court 1', 'badminton_court'): 1},
        "facilities",
        "facility_id",
        "source",
        2
    ),
    #timeslot already matches existing id = 1
    (
        {
            'start_time': datetime.time(20, 00, tzinfo=RA_CENTRE_TZ),
            'end_time': datetime.time(21, 0, tzinfo=RA_CENTRE_TZ),
            'day_of_week': 'Friday',
            'release_interval_days': 7,
        },
        {
            (
                datetime.time(20, 00, tzinfo=RA_CENTRE_TZ),
                datetime.time(21, 0, tzinfo=RA_CENTRE_TZ),
                "Friday",
                7
            ): 1
        },
        "timeslots",
        "timeslot_id",
        "source",
        1
    ),
    #timeslot doesn't matches existing id = 1
    (
        {
            'start_time': datetime.time(20, 00, tzinfo=RA_CENTRE_TZ),
            'end_time': datetime.time(21, 0, tzinfo=RA_CENTRE_TZ),
            'day_of_week': 'Saturday',
            'release_interval_days': 7,
        },
        {
            (
                datetime.time(20, 00, tzinfo=RA_CENTRE_TZ),
                datetime.time(21, 0, tzinfo=RA_CENTRE_TZ),
                "Friday",
                7
            ): 1
        },
        "timeslots",
        "timeslot_id",
        "source",
        2
    ),
)

#(data in, facility_id, timeslot_id, id out)
LOAD_SLOT_EVENTS_BATCH_TEST_CONSTANT = (
    #slot event exactly matches existing record, with scraped_datetime greater than previous
    (
        [
            {
                'num_people': 1,
                'scraped_datetime': datetime.datetime(2026, 4, 26, 7, 2, tzinfo=RA_CENTRE_TZ),
                'week_number': 6,
                'facility_id': 1,
                'timeslot_id': 1
            },
            {
                'num_people': 0,
                'scraped_datetime': datetime.datetime(2026, 4, 26, 7, 2, tzinfo=RA_CENTRE_TZ),
                'week_number': 6,
                'facility_id': 1,
                'timeslot_id': 1
            }
        ],
        [1, 2]
    ),
    #slot event exactly matches existing record except num_people, with scraped_datetime greater than previous
)

# data,expected_data_dict
PROCESS_SINGLE_DATA_TEST_CONSTANT = (
    # copy of what's in the db already
    (
        SAMPLE_RAW_JSON,
        None
    ),
    # copy of what's in the db already with just a different number of people
    (
        {
            "facilityName": "Badminton Court 1",
            "name": "Badminton Court 1 - Friday  Feb 07 - 3:00 PM",
            "numPeople": 0,
            "regStart": 1738332000000,
            "schedule": [
                {
                    "endDatetime": 1738962000000,
                    "startDatetime": 1738958400000,
                    "subject": "Badminton Court 1 - Friday  Feb 07 - 3:00 PM"
                }
            ],
        },
        {
            'num_people': 0,
            'week_number': 6,
            'facility_id': 1,
            'timeslot_id': 1
        }
    ),
    # new facility
    (
        {
            "facilityName": "Badminton Court 0",
            "name": "Badminton Court 0 - Friday  Feb 07 - 3:00 PM",
            "numPeople": 1,
            "regStart": 1738332000000,
            "schedule": [
                {
                    "endDatetime": 1738962000000,
                    "startDatetime": 1738958400000,
                    "subject": "Badminton Court 0 - Friday  Feb 07 - 3:00 PM"
                }
            ],
        },
        {
            'num_people': 0,
            'week_number': 6,
            'facility_id': 2,
            'timeslot_id': 1
        }
    ),
)