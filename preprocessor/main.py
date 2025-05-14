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

from psycopg import Error as PostgreSQLError

from src.setup import db_connect, load_env_file, get_s3_bucket, LOCAL_TZ, DB_TZ
from src.parser import DataValidationError
from src.download import get_s3_object_names, get_s3_json_data
from src.upload import get_list_of_unprocessed_object_names, process_and_load_batch_data

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
    file_handler = logging.FileHandler(
        filename=(Path(__file__).parent / "logs" / "log.log"), mode='w')
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
    # pylint: disable=too-many-locals, too-many-branches, line-too-long, too-many-statements, broad-exception-caught

    #setup env and connections
    _ = load_env_file(str(Path(__file__).parent) + "/.env")
    logger.info("connecting to DB.")
    server, conn = db_connect()

    if conn:
        logger.info("DB connection established.")

        inserted_datetime = datetime.now(tz=DB_TZ)
        logger.info("retreiving list of available S3 objects")
        s3_bucket = get_s3_bucket(override_s3_bucket)
        objects_list = get_s3_object_names(bucket=s3_bucket)
        new_objects_list = get_list_of_unprocessed_object_names(objects_list, conn)

        if new_objects_list:
            logger.info(
                f"preparing to process {len(new_objects_list)} "
                f"new objects out of {len(objects_list)}."
                )
        else:
            logger.info("No new objects found. Will shut down.")

        event_ids = []
        try:
            for object_name in new_objects_list:
                # get the raw data from s3
                logger.info(f"retreiving single s3 object {object_name}")
                data = get_s3_json_data(bucket=s3_bucket, object_name=object_name)

                event_ids += process_and_load_batch_data(
                    data=data,
                    object_name=object_name,
                    inserted_datetime=inserted_datetime,
                    conn=conn,
                    dry_run=dry_run)

        # if there's an exception flush the event_ids list because we're going to rollback everything
        except DataValidationError as e:
            logger.exception(f"A data validation error was detected: {e}")
            event_ids = []
        except PostgreSQLError as e:
            logger.exception(f"An error occured with the database: {e}")
            event_ids = []
        except Exception as e:
            logger.exception(f"an unhandled exception occured: {e}")
            conn.close() # pylint: disable=no-member
            if server:
                server.stop()
            event_ids = []
        finally:
            conn.close() # pylint: disable=no-member
            if server:
                server.stop()

    else:
        logger.error("No DB Connection")
    return event_ids

if __name__ == "__main__":
    # set a local variable to prod and call this main script to do manual initial
    # DB population or manual backfils
    #ra-center-raw-data-prod
    _ = main(dry_run=True)
