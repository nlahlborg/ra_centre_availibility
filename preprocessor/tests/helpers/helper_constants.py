"""
short simple unit test fixtures
"""
#pylint: disable=import-error, wrong-import-position, line-too-long
import sys
from pathlib import Path
sys.path.insert(1, str(Path(__file__).parent.parent.parent))
import datetime
from src.setup import API_TZ, WEB_DISPLAY_TZ, DB_TZ
from src.parser import DataValidationError

OLDER_DATETIME = DB_TZ.localize(datetime.datetime(2020,1,1,0,1))
MEDIUM_DATETIME = DB_TZ.localize(datetime.datetime(2025,1,27,0,1))
NEWER_DATETIME = DB_TZ.localize(datetime.datetime(2026,1,1,0,1))

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
    'end_time': DB_TZ.localize(datetime.datetime(2025, 2, 7, 21, 0)).timetz(),
    'facility_name': 'Badminton Court 1',
    'facility_type': 'badminton_court',
    'num_people': 1,
    'release_interval_days': 7,
    'scraped_datetime': DB_TZ.localize(datetime.datetime(2025, 1, 26, 7, 2)),
    'start_time': DB_TZ.localize(datetime.datetime(2025, 2, 7, 20, 0)).timetz(),
    'week_number': 6
}

SAMPLE_FACILITIES_DATA = {
    'facility_name': 'Badminton Court 1',
    'facility_type': 'badminton_court'
}

SAMPLE_TIMESLOTS_DATA = {
    'start_time': DB_TZ.localize(datetime.datetime(2025, 2, 7, 20, 0)).timetz(),
    'end_time': DB_TZ.localize(datetime.datetime(2025, 2, 7, 21, 0)).timetz(),
    'day_of_week': 'Friday',
    'release_interval_days': 7
}

SAMPLE_EVENTS_DATA = {
    'num_people': 1,
    'scraped_datetime': DB_TZ.localize(datetime.datetime(2025, 1, 26, 7, 2)),
    'week_number': 6,
}

#min start_datetime, expected
GET_SQL_RESERVATION_SYSTEM_EVENTS_TABLE_TEST_CONSTANT = (
    # basecase valid mindatetime provided
    (
        '20250126T000200Z',
        [
            (2, 1, 6, 1, 1),
            (3, 0, 7, 1, 1),
        ]
    ),
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
    (
        DB_TZ.localize(datetime.datetime(2025, 2, 7, 20, 0)).timetz(),
        DB_TZ.localize(datetime.datetime(2025, 2, 7, 21, 0)).timetz(),
        'Friday',
        7
    ): 1
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
        DB_TZ.localize(datetime.datetime(2025, 1, 26, 0, 2, 0))
    ),
    #yes daylight savings
    (
        "raw_centre_raw_20250502T020513Z.json", 
        "raw_centre_raw_", 
        DB_TZ.localize(datetime.datetime(2025, 5, 2, 2, 5, 13))
    )
)

# "data,scraped_datetime,expected_facility_data,expected_timeslot_data,expected_event_data"
PARSE_DATA_TEST_CONSTANT = (
    (
        SAMPLE_RAW_JSON,
        DB_TZ.localize(datetime.datetime(2025, 1, 26, 7, 2)),
        SAMPLE_FACILITIES_DATA,
        SAMPLE_TIMESLOTS_DATA,
        SAMPLE_EVENTS_DATA
    ),
    (
        {
            "facilityName": "Badminton Court 1",
            "name": "Badminton Court 1 - Friday  Feb 14 - 3:00 PM",
            "numPeople": 0,
            "regStart": 1738929600000,
            "schedule": [
                {
                    "endDatetime": 1739566800000,
                    "startDatetime": 1739563200000
                }
            ],
        },
        DB_TZ.localize(datetime.datetime(2025, 1, 26, 7, 2)),
        SAMPLE_FACILITIES_DATA,
        {
            'start_time': DB_TZ.localize(datetime.datetime(2025, 2, 14, 20, 0)).timetz(),
            'end_time': DB_TZ.localize(datetime.datetime(2025, 2, 14, 21, 0)).timetz(),
            'day_of_week': 'Friday',
            'release_interval_days': 7
        },
        {
            'num_people': 0,
            'scraped_datetime': DB_TZ.localize(datetime.datetime(2025, 1, 26, 7, 2)),
            'week_number': 7,
        }
    )
)

PARSE_DISPLAY_NAME_TEST_CONSTANT = (
    (
        "Badminton Court 1 - Friday  Feb 07 - 3:00 PM",
        2025,
        WEB_DISPLAY_TZ.localize(datetime.datetime(2025, 2, 7, 15, 0))
    ),    
    (
        "Badminton Court 1 - Friday Feb 07 - 3:00 PM",
        2025,
        WEB_DISPLAY_TZ.localize(datetime.datetime(2025, 2, 7, 15, 0))
    ),    
    (
        "Pickleball Centre - Friday Feb 07 - 3:00 PM",
        2025,
        WEB_DISPLAY_TZ.localize(datetime.datetime(2025, 2, 7, 15, 0))
    ),
    (
        "Photo Studio Booking- Saturday  Apr 26 - 7:00 AM",
        2025,
        WEB_DISPLAY_TZ.localize(datetime.datetime(2025, 4, 26, 7, 0))
    )
)

FLAG_INCONSISTANT_DATETIME_TEST_CONSTANT = (
    # correct flagging of correct parsing
    (
        WEB_DISPLAY_TZ.localize(datetime.datetime(2025, 2, 7, 15, 0)),
        "Badminton Court 1 - Friday  Feb 07 - 3:00 PM",
        True
    ),
    # assuming an incorrect timezone for the startdatetime will produce an error
    (
        API_TZ.localize(datetime.datetime(2025, 2, 7, 15, 0)),
        "Badminton Court 1 - Friday  Feb 07 - 3:00 PM",
        DataValidationError
    ),
    # A startdatetime that is inconsistent with the displayname will produce an error
    (
        WEB_DISPLAY_TZ.localize(datetime.datetime(2025, 2, 7, 12, 0)),
        "Badminton Court 1 - Friday  Feb 07 - 3:00 PM",
        DataValidationError
    ),
)

FLAG_STALE_START_DATETIME_TEST_CONSTANT = (
    #scraped_datetime is older than start_datetime
    (
        API_TZ.localize(datetime.datetime(2025, 2, 7, 15, 0)),
        OLDER_DATETIME,
        True
    ),
    #scraped_datetime is newer than start_datetime by less than 1 day
    (
        API_TZ.localize(datetime.datetime(2025, 2, 7, 15, 0)),
        API_TZ.localize(datetime.datetime(2025, 2, 7, 15, 1)),
        True
    ),
    #scraped_datetime is newer than start_datetime by more than 1 day
    (
        API_TZ.localize(datetime.datetime(2025, 2, 7, 15, 0)),
        NEWER_DATETIME,
        DataValidationError
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
        (
            DB_TZ.localize(datetime.datetime(2025, 2, 7, 20, 0)).timetz(),
            DB_TZ.localize(datetime.datetime(2025, 2, 7, 21, 0)).timetz(),
            'Friday',
            7
        )
    )
)

GENERATE_INSERT_SQL_BATCH_TEST_CONSTANT = (
    (
        [SAMPLE_EVENTS_DATA.copy(), SAMPLE_EVENTS_DATA.copy()],
        "reservation_system_events",
        '''INSERT INTO "source"."reservation_system_events" ("num_people", "scraped_datetime", "week_number")
            VALUES (%s, %s, %s)''',
        [
            (1, DB_TZ.localize(datetime.datetime(2025, 1, 26, 7, 2)), 6),
            (1, DB_TZ.localize(datetime.datetime(2025, 1, 26, 7, 2)), 6)
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
            'start_time': DB_TZ.localize(datetime.datetime(2025, 2, 7, 20, 0)).timetz(),
            'end_time': DB_TZ.localize(datetime.datetime(2025, 2, 7, 21, 0)).timetz(),
            'day_of_week': 'Friday',
            'release_interval_days': 7,
        },
        {
            (
                DB_TZ.localize(datetime.datetime(2025, 2, 7, 20, 0)).timetz(),
                DB_TZ.localize(datetime.datetime(2025, 2, 7, 21, 0)).timetz(),
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
            'start_time': DB_TZ.localize(datetime.datetime(2025, 2, 8, 20, 0)).timetz(),
            'end_time': DB_TZ.localize(datetime.datetime(2025, 2, 8, 21, 0)).timetz(),
            'day_of_week': 'Saturday',
            'release_interval_days': 7,
        },
        {
            (
                DB_TZ.localize(datetime.datetime(2025, 2, 8, 20, 0)).timetz(),
                DB_TZ.localize(datetime.datetime(2025, 2, 8, 21, 0)).timetz(),
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

#(datas in, ids out)
LOAD_SLOT_EVENTS_BATCH_TEST_CONSTANT = (
    #multiple items
    (
        [
            {
                'num_people': 1,
                'scraped_datetime': DB_TZ.localize(datetime.datetime(2026, 1, 26, 7, 10)),
                'week_number': 6,
                'facility_id': 1,
                'timeslot_id': 1
            }, 
            {
                'num_people': 0,
                'scraped_datetime': DB_TZ.localize(datetime.datetime(2026, 1, 26, 7, 10)),
                'week_number': 7,
                'facility_id': 1,
                'timeslot_id': 1
            }
        ],
        [4,5]
    ),
    #just one item
    (
        [
            {
                'num_people': 0,
                'scraped_datetime': DB_TZ.localize(datetime.datetime(2026, 1, 26, 7, 10)),
                'week_number': 6,
                'facility_id': 1,
                'timeslot_id': 1
            }
        ],
        [4]
    ),
)

# data,events_table_ids_dict,scraped_datetime,expected_data_dict
PROCESS_SINGLE_DATA_TEST_CONSTANT = (
    # copy of most recent record in db already and scraped_datetime is before start datetime
    (
         {
            "facilityName": "Badminton Court 1",
            "name": "Badminton Court 1 - Friday  Feb 07 - 3:00 PM",
            "numPeople": 1,
            "regStart": 1738332000000,
            "schedule": [
                {
                    "endDatetime": 1738962000000,
                    "startDatetime": 1738958400000
                }
            ],
        },
        GET_RESERVATION_SYSTEM_EVENTS_IDS_DICT_TEST_CONSTANT,
        MEDIUM_DATETIME,
        None
    ),
    # copy of what's in the db already and scraped_datetime is after start datetime (invalid)
    (
        {
            "facilityName": "Badminton Court 1",
            "name": "Badminton Court 1 - Friday  Feb 07 - 3:00 PM",
            "numPeople": 1,
            "regStart": 1738332000000,
            "schedule": [
                {
                    "endDatetime": 1738962000000,
                    "startDatetime": 1738958400000
                }
            ],
        },
        GET_RESERVATION_SYSTEM_EVENTS_IDS_DICT_TEST_CONSTANT,
        NEWER_DATETIME,
        DataValidationError
    ),
    # copy of what's in the db already with a newer scraped datetime but a different number of people
    (
        {
            "facilityName": "Badminton Court 1",
            "name": "Badminton Court 1 - Friday  Feb 07 - 3:00 PM",
            "numPeople": 0,
            "regStart": 1738332000000,
            "schedule": [
                {
                    "endDatetime": 1738962000000,
                    "startDatetime": 1738958400000
                }
            ],
        },
        GET_RESERVATION_SYSTEM_EVENTS_IDS_DICT_TEST_CONSTANT,
        MEDIUM_DATETIME,
        {
            'num_people': 0,
            'week_number': 6,
            'facility_id': 1,
            'timeslot_id': 1,
            'scraped_datetime': MEDIUM_DATETIME
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
                    "startDatetime": 1738958400000
                }
            ],
        },
        GET_RESERVATION_SYSTEM_EVENTS_IDS_DICT_TEST_CONSTANT,
        MEDIUM_DATETIME,
        {
            'num_people': 1,
            'week_number': 6,
            'facility_id': 2,
            'timeslot_id': 1,
            'scraped_datetime': MEDIUM_DATETIME
        }
    ),
    # TODO create a mechanism to upload no data if startdatetime is stale
)

# data, object_name, expected
PROCESS_AND_LOAD_BATCH_DATA_TEST_CONSTANT = (
    # basecase: both are new data and the startdatetimes are not stale
    (
        [
            {
                "facilityName": "Badminton Court 1",
                "name": "Badminton Court 1 - Friday  Feb 07 - 3:00 PM",
                "numPeople": 2,
                "regStart": 1738332000000,
                "schedule": [
                    {
                        "endDatetime": 1738962000000,
                        "startDatetime": 1738958400000
                    }
                ],
            },
            {
                "facilityName": "Badminton Court 1",
                "name": "Badminton Court 1 - Friday  Feb 14 - 3:00 PM",
                "numPeople": 2,
                "regStart": 1738929600000,
                "schedule": [
                    {
                        "endDatetime": 1739566800000,
                        "startDatetime": 1739563200000
                    }
                ],
            },
        ],
        "raw_centre_raw_20250126T000200Z.json",
        [4,5]
    ),
    # both data are repeats of the previous row and the startdatetimes are not stale
    (
        [
            {
                "facilityName": "Badminton Court 1",
                "name": "Badminton Court 1 - Friday  Feb 07 - 3:00 PM",
                "numPeople": 1,
                "regStart": 1738332000000,
                "schedule": [
                    {
                        "endDatetime": 1738962000000,
                        "startDatetime": 1738958400000
                    }
                ],
            },
            {
                "facilityName": "Badminton Court 1",
                "name": "Badminton Court 1 - Friday  Feb 14 - 3:00 PM",
                "numPeople": 0,
                "regStart": 1738929600000,
                "schedule": [
                    {
                        "endDatetime": 1739566800000,
                        "startDatetime": 1739563200000
                    }
                ],
            },
        ],
        "raw_centre_raw_20250126T000200Z.json",
        []
    ),
    # single data is a repeat
    (
        [
            {
                "facilityName": "Badminton Court 1",
                "name": "Badminton Court 1 - Friday  Feb 07 - 3:00 PM",
                "numPeople": 1,
                "regStart": 1738332000000,
                "schedule": [
                    {
                        "endDatetime": 1738962000000,
                        "startDatetime": 1738958400000
                    }
                ],
            }
        ],
        "raw_centre_raw_20250126T000200Z.json",
        []
    ),
    # single data is a repeat
    (
        [
            {
                "facilityName": "Badminton Court 1",
                "name": "Badminton Court 1 - Friday  Feb 14 - 3:00 PM",
                "numPeople": 0,
                "regStart": 1738929600000,
                "schedule": [
                    {
                        "endDatetime": 1739566800000,
                        "startDatetime": 1739563200000
                    }
                ],
            },
        ],
        "raw_centre_raw_20250126T000200Z.json",
        []
    ),
)
