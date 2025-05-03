"""
web_scraper.src.web_query

This module provides functions to interact with the RA Centre website. It includes
functions to query the website, extract context authentication information, construct
payloads for POST requests, and retrieve availability data for various programs.
"""

import re
import json
from math import floor, ceil
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
import logging

import urllib3

logger = logging.getLogger("web_query")

http = urllib3.PoolManager()
URL = "https://theracentre.my.site.com"
PROGRAM_CODES = (
    "PROG-000317", "PROG-000003", #badminton
    "PROG-000110", "PROG-000074", #pickleball
    "PROG-000071", #squash
    "PROG-000072", #raquetball
    "PROG-000415", #curling
    "PROG-000005", #archery
    "PROG-000090" #photo studio
)

def query(
    url: str=URL,
    method: str="GET",
    headers: Optional[dict]=None,
    payload: Optional[dict]=None
    ) -> urllib3.response.BaseHTTPResponse:
    """
    Query the RAC website
    """
    if headers is None:
        headers = {"Referer": URL}

    if method == "GET":
        r = http.request("GET", url, headers=headers)
        return r.status, r.data.decode('utf-8')

    if method == "POST":
        r = http.request("POST", url, headers=headers, json=payload)
        return r.status, r.data.decode('utf-8')

    return None

def get_context_auth(text: str) -> dict | None:
    """
    attempt to appear less bot-ish by making a get request 
    to the website and parsing the html result to get session specific info
    """
    regex_str = r"(?:\()({\"vf\":.*)(?:\)\);)"
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
    status, response_text = query(url=URL, method="GET")

    if status == 200:
        action="ts_avo.AvocadoSiteController"
        context = get_context_auth(response_text)
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

    return None

def get_availability(
    start_date: datetime=datetime.now().astimezone(),
    end_date: datetime=datetime.now() + timedelta(days=60),
    program_codes: Tuple[str]=PROGRAM_CODES
    ) -> dict | None:
    """
    gets the availability of the programs
    """
    payload = construct_payload(start_date, end_date, program_codes)
    service = payload.pop("service")

    status, response_text = query(
        url=URL+f"/{service}",
        headers={"Referer": "https://theracentre.my.site.com/"},
        method="POST",
        payload=payload
        )

    if status == 200:
        return json.loads(response_text)

    if status != 200:
        logger.exception(f"Failed to response payload with return code {status}")

    return None
