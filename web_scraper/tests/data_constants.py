"""
constants to use in tests
"""
# pylint: disable=line-too-long
import datetime
from pytz import UTC

HTML_PAYLOAD_SAMPLE = """
<!DOCTYPE HTML>

<!--[if lt IE 7]>     <html lang="en" ng-app="app" class="no-js lt-ie9 lt-ie8 lt-ie7"> <![endif]-->
<!--[if IE 7]>        <html lang="en" ng-app="app" class="no-js lt-ie9 lt-ie8"> <![endif]-->
<!--[if IE 8]>        <html lang="en" ng-app="app" class="no-js lt-ie9"> <![endif]-->

<html class="no-js" lang="en" ng-app="app">

}(window.UITheme = window.UITheme || {}));</script><script type="text/javascript">
Visualforce.remoting.Manager.add(new $VFRM.RemotingProviderImpl({"vf":{"vid":"0664x00000AprDY","xhr":False,"dev":False,"tst":False,"dbg":False,"tm":1738964618683,"ovrprm":False},"actions":{"ts_avo.AvocadoSiteController":{"ms":[{"name":"dispatch","len":2,"ns":"ts_avo","ver":43.0,"csrf":"sampleCSRF0=","authorization":"sampleAUTH0.morechars1="}],"prm":0}},"service":"apexremote"}));
</script><meta HTTP-EQUIV="PRAGMA" CONTENT="NO-CACHE" />
"""

RESPONSE_DATA_SAMPLE = [
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
    {'ageMaxInYears': 130,
     'ageMinInYears': 12,
     'barcode': '414373',
     'code': 'INST-414373',
     'divisionCode': 'DIV-002',
     'endDate': 1741910400000,
     'facilityName': 'Squash Court 5',
     'hasRegEarlyStarted': True,
     'hasRegEnded': False,
     'hasRegPriorityStarted': True,
     'hasRegReturnStarted': True,
     'hasRegStarted': True,
     'instanceType': 'Requires_Registration',
     'isLite': True,
     'isPackage': False,
     'locationCode': 'LOC-000002',
     'locationName': 'The RA Centre',
     'makeupClassesEnabled': False,
     'marketingDescription': 'One-hour court rentals are available for all Non-RA and RA Members.', 
     'maxAge': 130,
     'maxPeople': 1,
     'minAge': 12,
     'name': 'Squash Court 5 - Friday  Mar 14 - 1:30 PM',
     'numPeople': 0,
     'numWaitlist': 0,
     'programCode': 'PROG-000071',
     'regCancel': 1741800600000,
     'regEarly': 1741356000000,
     'regEnd': 1741975200000,
     'regPriority': 1741356000000,
     'regReturn': 1741356000000,
     'regStart': 1741356000000,
     'schedule': [
         {
             'description': '',
             'endDatetime': 1741977000000,
             'isRecurrence': False,
             'startDatetime': 1741973400000,
             'subject': 'Squash Court 5 - Friday  Mar 14 - 1:30 PM'
             }
             ],
    'startDate': 1741973400000,
    'tracksAttendance': False,
    'weekDays': [
        'Fri'
        ]
    }
]


EXPECTED_SLOT_IDS = ["202502071500_badminton_court_1", "202503141330_squash_court_5"]
EXPECTED_FACILITY_NAMES = ["badminton court", "squash court"]

EXISTING_DB_DATA = [
    {
        'slot_id': '202502161300_badminton_court_1',
        'facility_name': 'Badminton Court 1',
        'facility_type': None,
        'start_datetime': datetime.datetime(2025, 2, 16, 13, 0),
        'end_datetime': datetime.datetime(2025, 2, 16, 14, 0),
        'num_people': 0,
        'has_reg_ended': False,
        'inserted_datetime': datetime.datetime(2025, 2, 16, 20, 4, 8, 676798, tzinfo=UTC)
    },
    {
        'slot_id': '202502161300_badminton_court_2',
        'facility_name': 'Badminton Court 2',
        'facility_type': "badminton court",
        'start_datetime': datetime.datetime(2025, 2, 16, 13, 0),
        'end_datetime': datetime.datetime(2025, 2, 16, 14, 0),
        'num_people': 0,
        'has_reg_ended': False,
        'inserted_datetime': datetime.datetime(2025, 2, 16, 20, 4, 8, 676798, tzinfo=UTC)
    }
]

NEW_DB_DATA = [
    {
        'slot_id': '202502171300_badminton_court_1',
        'facility_name': 'Badminton Court 1',
        'facility_type': "badminton court",
        'start_datetime': datetime.datetime(2025, 2, 17, 13, 0),
        'end_datetime': datetime.datetime(2025, 2, 17, 14, 0),
        'num_people': 0,
        'has_reg_ended': False,
        'inserted_datetime': datetime.datetime(2025, 2, 16, 20, 4, 8, 676798, tzinfo=UTC)
    },
    {
        'slot_id': '202502171300_badminton_court_2',
        'facility_name': 'Badminton Court 2',
        'facility_type': "badminton court",
        'start_datetime': datetime.datetime(2025, 2, 17, 13, 0),
        'end_datetime': datetime.datetime(2025, 2, 17, 14, 0),
        'num_people': 0,
        'has_reg_ended': False,
        'inserted_datetime': datetime.datetime(2025, 2, 17, 20, 4, 8, 676798, tzinfo=UTC)
    }
]

CHANGED_DB_DATA = [
    {
        'slot_id': '202502161300_badminton_court_1',
        'facility_name': 'Badminton Court 1',
        'facility_type': 'badminton court',
        'start_datetime': datetime.datetime(2025, 2, 16, 13, 0),
        'end_datetime': datetime.datetime(2025, 2, 16, 14, 0),
        'num_people': 0,
        'has_reg_ended': False,
        'inserted_datetime': datetime.datetime(2025, 2, 17, 20, 4, 8, 676798, tzinfo=UTC)
    },
    {
        'slot_id': '202502161300_badminton_court_2',
        'facility_name': 'Badminton Court 2',
        'facility_type': 'badminton court',
        'start_datetime': datetime.datetime(2025, 2, 16, 13, 0),
        'end_datetime': datetime.datetime(2025, 2, 16, 14, 0),
        'num_people': 1,
        'has_reg_ended': False,
        'inserted_datetime': datetime.datetime(2025, 2, 17, 20, 4, 8, 676798, tzinfo=UTC)
    }
]
