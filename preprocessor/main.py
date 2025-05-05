"""
preprocessor.main

This module is the entry point for the preprocesser application
that reads json documents from S3 and transforms them into a 
a relational database (star) schema.
"""
from datetime import datetime
from pathlib import Path
import logging
from src.setup import db_connect, load_env_file, LOCAL_TZ
from src.upload import load_data

# Configure logging
logger = logging.getLogger("main")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
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
    """"
    main function for the preprocessor service

    Args:
        write_to_db: bool
            Set this to false when performing integration testing on production
            Set this to true all other times in order to write to DB
    
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
        retvar = load_data(conn, server, write_to_db)
    else:
        logger.error("No DB Connection")
    return retvar

if __name__ == "__main__":
    # set a local variable to prod and call this main script to do manual initial
    # DB population or manual backfils
    _ = main(write_to_db=True)
