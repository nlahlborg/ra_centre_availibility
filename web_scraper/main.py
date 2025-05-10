"""
web_scraper.main

This module is the entry point for the web scraping application that retrieves
availability data from the RA Centre website and saves it to S3 as a json file.
The main function orchestrates the entire process, including setting
up the environment, establishing database connections, scraping data, and
saving new data to the database.

Example:
    python main.py
"""
from datetime import datetime

import logging
import pytz

from src.web_query import get_availability
from src.upload import upload_to_s3
from src.setup import LOCAL_TZ, get_s3_bucket

# Configure logging
logger = logging.getLogger("main")
logger.setLevel(logging.INFO)

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create a custom formatter
class LocalTZFormatter(logging.Formatter):
    """
    custom logs formatter
    """
    def converter(self, timestamp):
        """
        convert timestamp to desired locale
        """
        db_dt = datetime.fromtimestamp(timestamp, LOCAL_TZ)
        pst_dt = db_dt.astimezone()
        return pst_dt.timetuple()

formatter = LocalTZFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(console_handler)

def main():
    """
    The main function that runs the web scraping and data saving process.

    This function orchestrates the entire process of retrieving availability data
    from the RA Centre website and optionally saving it to a MySQL database. It sets
    up the environment, establishes database connections, scrapes data, and saves new
    data to the database

    Returns:
        str: log string

    Raises:
        Exception: If an error occurs during the process, the exception is raised after
                   closing the database connection and stopping the SSH tunnel.
    """

    #scrape data
    logger.info("preparing to get courts availability data")

    timestamp = datetime.now(tz=pytz.utc).strftime("%Y%m%dT%H%M%SZ")
    response = get_availability()
    data = response[0]["result"]["data"]

    logger.info(f"received {len(data)} items from ra centre site")

    response = upload_to_s3(
        data,
        bucket_name=get_s3_bucket(),
        object_name=f"raw_centre_raw_{timestamp}.json"
        )

    if response[0]:
        logger.info(f"s3 upload response: {response}")
        s3_response = f"uploaded batch of {len(data)} records to s3"
    else:
        logger.error(f"s3 upload error details: {response}")
        s3_response = response[1]

    return s3_response

if __name__ == "__main__":
    _ = main()
