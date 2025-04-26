"""
web_scraper.main

This module is the entry point for the web scraping application that retrieves
availability data from the RA Centre website and optionally saves it to a MySQL
database. The main function orchestrates the entire process, including setting
up the environment, establishing database connections, scraping data, and
saving new data to the database.

Example:
    python main.py
"""
from pathlib import Path
from datetime import datetime

import logging
import pytz

from src.web_query import get_availability
from src.parser import parse_availability_data
from src.upload import get_only_new_data, prepare_transaction, save_data, upload_to_s3
from src.setup import LOCAL_TZ, db_connect, load_env_file, get_s3_bucket

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

def main(write_to_db=False):
    """
    The main function that runs the web scraping and data saving process.

    This function orchestrates the entire process of retrieving availability data
    from the RA Centre website and optionally saving it to a MySQL database. It sets
    up the environment, establishes database connections, scrapes data, and saves new
    data to the database if the `write_to_db` argument is set to True.

    Args:
        write_to_db (bool): A flag to control whether the scraped data should be saved
                            to the MySQL database. Defaults to False.

    Returns:
        int: The number of new rows saved to the MySQL database.

    Raises:
        Exception: If an error occurs during the process, the exception is raised after
                   closing the database connection and stopping the SSH tunnel.
    """
    #setup env and connections
    _ = load_env_file(str(Path(__file__).parent) + "/.env")
    server, conn = db_connect()

    #scrape data
    logger.info(f"received value for write_to_db: {write_to_db}")
    logger.info("preparing to get courts availability data")

    timestamp = datetime.now(tz=pytz.utc).strftime("%Y%m%dT%H%M%SZ")
    response = get_availability()
    data = response[0]["result"]["data"]
    dict_list = parse_availability_data(data)

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

    #save to mysql
    try:
        data_new = get_only_new_data(dict_list, conn)
        n_rows = len(data_new)
        logger.info(f"Number of new rows for mysql: {n_rows}")

        if n_rows > 0 and write_to_db:
            logger.info("saving data to the mysql database")
            sql = prepare_transaction(data_new)
            save_data(sql, conn)
        elif not write_to_db:
            logger.info(f"did not write data because write_to_db = {write_to_db}")
            n_rows = 0
        else:
            logger.info("no new data to save for mysql")

        conn.close()
        server.stop()

        return n_rows, s3_response

    except Exception as e:
        conn.close()
        server.stop()
        raise e

if __name__ == "__main__":
    _ = main()
