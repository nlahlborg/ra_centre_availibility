from src.query import get_availability
from src.parser import parse_availability_data
from src.upload import prepare_transaction

import logging
from logging.handlers import TimedRotatingFileHandler
import os

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

# Create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

if __name__ == "__main__":
    logger.info("preparing to get availability data")
    response = get_availability()
    data = response[0]["result"]["data"]
    df = parse_availability_data(data)
    transaction_string, n_rows = prepare_transaction(df)
    logger.info(f"Number of new rows: {n_rows}")

    if n_rows > 0:
        logger.info("saving data to the database")
        save_data(transaction_string)
    else:
        logger.info("no new data to save")
