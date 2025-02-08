"""
functions to talk to the RAC website
"""

import requests
from datetime import datetime, timedelta
from typing import List, Optional
import re
import json
import logging
from math import floor, ceil

logger = logging.getLogger("web_query")

URL = "https://theracentre.my.site.com"

def query(
    url: str=URL, 
    method: str="GET",
    headers: Optional[dict]=None, 
    payload: Optional[dict]=None
    ) -> requests.models.Response:
    """
    Query the RAC website
    """
    if headers is None:
        headers = {"Referer": URL}

    if method == "GET":
        r = requests.get(url, headers=headers)
    elif method == "POST":
        r = requests.post(url, headers=headers, json=payload)

    return r

def get_context_auth(text: str) -> dict | None:
    """
    gets the payload context information by making a get request to the website and 
    parsing the html result
    """
    regex_str = "(?:\()({\"vf\":.*)(?:\)\);)"
    json_string = re.findall(regex_str, text)[0]

    try:
        json_obj = json.loads(json_string)
        return json_obj  
    except json.JSONDecodeError:
        logger.exception("Failed to decode the context auth json")
        return None

def construct_payload(
    start_date: datetime, 
    end_date: datetime, 
    program_codes: List[str]
    ) -> dict | None:
    """
    constructs the payload for the post request
    """
    #initialize payload with constants
    payload = {
        "type": "rpc",
        "tid": 11,
    }

    #get the context auth    
    r = query(url=URL, method="GET")

    if r.status_code:
        action="ts_avo.AvocadoSiteController"
        context = get_context_auth(r.text)
        payload["action"] = action
        payload["method"] = context["actions"][action]["ms"][0]["name"]
        payload["ctx"] = {}
        payload["ctx"]["csrf"] =  context["actions"][action]["ms"][0]["csrf"]
        payload["ctx"]["ns"] =  context["actions"][action]["ms"][0]["ns"]
        payload["ctx"]["ver"] =  int(context["actions"][action]["ms"][0]["ver"])

        #get the vid
        payload["ctx"]["vid"] = context["vf"]["vid"]

        #get the service
        payload["service"] = context["service"]

        #construct data
        data = [
            "findInstances",
            json.dumps(
                    {
                        "searchText": "",
                        "programCodes": program_codes,
                        "division": None,
                        "locationCode": "LOC-000002",
                        "sessionCode": "",
                        "active": True,
                        "recordTypeDevNames": [
                            "No_Registration",
                            "Requires_Registration"
                        ],
                        "isPackage": False,
                        "lite": True,
                        "instanceCodes": None,
                        "weekDays": None,
                        "startDate": int(floor(start_date.timestamp()/86400)*86400*1000),
                        "endDate": int(ceil(end_date.timestamp()/86400)*86400*1000),
                        "__avoLang": "en"
                }
            )
        ]
        payload["data"] = data

        return payload
    else:
        logger.exception(f"Failed to get the context auth with return code {r.status_code}")
        return None

def get_availability(
    start_date: datetime=datetime.now(), 
    end_date: datetime=datetime.now() + timedelta(days=60), 
    program_codes: List[str]=["PROG-000317","PROG-000003"]
    ) -> dict | None:
    """
    gets the availability of the programs
    """
    payload = construct_payload(start_date, end_date, program_codes)
    service = payload.pop("service")

    r = query(
        url=URL+f"/{service}", 
        headers={"Referer": "https://theracentre.my.site.com/"}, 
        method="POST", 
        payload=payload
        )

    if r.status_code == 200:
        return r.json()
    else:
        logger.exception(f"Failed to response payload with return code {r.status_code}")
        return None



