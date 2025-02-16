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

RESPONSE_DATA_SAMPLE_BADMINTON = [
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
    }
]