from datetime import datetime, UTC
from pathlib import Path

from src.web_query import get_availability
from src.parser import parse_availability_data
from src.upload import get_only_new_data, prepare_transaction, save_data
from src.setup import load_env_file, DB_TZ, db_connect

import logging
#from logging.handlers import TimedRotatingFileHandler

load_env_file(str(Path(__file__).parent / ".env"))

# Create logs directory if it doesn't exist
# if not os.path.exists('logs'):
#     os.makedirs('logs')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")
logger.setLevel(logging.INFO)

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create file handler which logs even debug messages
# file_handler = TimedRotatingFileHandler('logs/app.log', when='midnight', interval=1, backupCount=7)
# file_handler.setLevel(logging.INFO)
# file_handler.suffix = "%Y-%m-%d"

# Create a custom formatter
class PSTFormatter(logging.Formatter):
    def converter(self, timestamp):
        utc_dt = datetime.fromtimestamp(timestamp, UTC)
        pst_dt = utc_dt.astimezone(DB_TZ)
        return pst_dt.timetuple()  # Return a time tuple

formatter = PSTFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
# file_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(console_handler)
# logger.addHandler(file_handler)

def main():
    #scrape data
    logger.info("preparing to get availability data")
    response = get_availability()
    data = response[0]["result"]["data"]
    dict_list = parse_availability_data(data)
    logger.info(f"received {len(dict_list)} items from ra centre site")

    #save to mysql
    server, conn = db_connect()
    try:
        data_new = get_only_new_data(dict_list, conn)
        n_rows = len(data_new)
        logger.info(f"Number of new rows for mysql: {n_rows}")

        if n_rows > 0:
            logger.info("saving data to the mysql database")
            sql = prepare_transaction(data_new)
            save_data(sql, conn)
        else:
            logger.info("no new data to save for mysql")

        conn.close()
        server.stop()

        return n_rows
    
    except Exception as e:
        conn.close()
        server.stop()
        raise(e)

if __name__ == "__main__":
    _ = main()
