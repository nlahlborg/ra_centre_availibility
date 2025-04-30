"""
web_scraper.src.setup

This module provides the setup and configuration for the web scraping application.
It includes functions to load environment variables, retrieve database passwords,
and establish SSH tunnels and MySQL database connections.
"""

import os
import logging

import pytz

logger = logging.getLogger("setup")
LOCAL_TZ = pytz.timezone('US/Pacific')

def get_s3_bucket():
    """
    return the correct s3 bucket for prod and dev deployments
    """
    my_env = os.environ.get("ENV", "dev")
    if my_env == "prod":
        s3_bucket = "ra-center-raw-data-prod"
    else:
        s3_bucket = "ra-center-raw-data-dev"

    return s3_bucket
