"""
preprocessor.main

This module is the entry point for the preprocesser application
that reads json documents from S3 and transforms them into a 
a relational database (star) schema.
"""
import os
from datetime import datetime
from pathlib import Path
import logging
from src.setup import db_connect, load_env_file, LOCAL_TZ
from src.upload import load_data

LOG_TO_FILE = os.environ.get("LOG_TO_FILE", False)

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create console handler
console_handler = logging.StreamHandler()

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

formatter = LocalTZFormatter('%(asctime)s.%(msecs)03d  - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(console_handler)

#if we're running locally create a file handler
if LOG_TO_FILE:
    file_handler = logging.FileHandler(filename=(Path(__file__).parent / "logs" / "log.log"), mode='w')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)


def main(dry_run=True, override_s3_bucket=False):
    """"
    main function for the preprocessor service

    Args:
        dry_run: bool
            Set this to True when performing integration testing on production
            Set this to False all other times in order to write to DB
    
    Returns:
        List of ids corresponding to data that was uploaded to the Postgresql DB,
        otherwise empty list
    
    """
    #setup env and connections
    _ = load_env_file(str(Path(__file__).parent) + "/.env")
    logger.info("connecting to DB.")
    server, conn = db_connect()

    retvar = False
    if conn:
        logger.info("DB connection established.")
        retvar = load_data(conn, server, dry_run, override_s3_bucket)
    else:
        logger.error("No DB Connection")
    return retvar

if __name__ == "__main__":
    # set a local variable to prod and call this main script to do manual initial
    # DB population or manual backfils
    #ra-center-raw-data-prod
    _ = main(dry_run=False, override_s3_bucket="ra-center-raw-data-prod")
