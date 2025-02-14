import os
from datetime import datetime, UTC
from pathlib import Path
from sqlalchemy import create_engine

from src.web_query import get_availability
from src.parser import parse_availability_data
from src.upload import compare_data
from src.setup import load_env_file, get_mysql_connect_string, TZ

import logging
from logging.handlers import TimedRotatingFileHandler

load_env_file(str(Path(__file__).parent / ".env"))
ENGINE = create_engine(get_mysql_connect_string())

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")
logger.setLevel(logging.INFO)

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create file handler which logs even debug messages
file_handler = TimedRotatingFileHandler('logs/app.log', when='midnight', interval=1)
file_handler.setLevel(logging.INFO)
file_handler.suffix = "%Y-%m-%d"

# Create a custom formatter
class PSTFormatter(logging.Formatter):
    def converter(self, timestamp):
        utc_dt = datetime.fromtimestamp(timestamp, UTC)
        pst_dt = utc_dt.astimezone(TZ)
        return pst_dt.timetuple()  # Return a time tuple

formatter = PSTFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

if __name__ == "__main__":
    #scrape data
    logger.info("preparing to get availability data")
    response = get_availability()
    data = response[0]["result"]["data"]
    df = parse_availability_data(data)

    #save to mysql
    df_new = compare_data(df, ENGINE)
    n_rows = df_new.shape[0]
    logger.info(f"Number of new rows for mysql: {n_rows}")

    if n_rows > 0:
        logger.info("saving data to the mysql database")
        df_new.to_sql("badminton_courts", ENGINE, if_exists="append")
    else:
        logger.info("no new data to save for mysql")
