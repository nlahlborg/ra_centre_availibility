from pathlib import Path
from datetime import datetime
from src.setup import DB_TZ

import logging

# Configure logging
logger = logging.getLogger("main")
logger.setLevel(logging.INFO)

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create a custom formatter
class LocalTZFormatter(logging.Formatter):
    def converter(self, timestamp):
        db_dt = datetime.fromtimestamp(timestamp, DB_TZ)
        pst_dt = db_dt.astimezone()
        return pst_dt.timetuple() 

formatter = LocalTZFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(console_handler)

def main(write_to_db=False):
    from src.web_query import get_availability
    from src.parser import parse_availability_data
    from src.upload import get_only_new_data, prepare_transaction, save_data
    from src.setup import db_connect, load_env_file

    #setup env and connections
    _ = load_env_file(str(Path(__file__).parent) + "/.env")
    server, conn = db_connect()

    #scrape data
    logger.info(f"received value for write_to_db: {write_to_db}")
    logger.info("preparing to get courts availability data")
    
    response = get_availability()
    data = response[0]["result"]["data"]
    dict_list = parse_availability_data(data)
    
    logger.info(f"received {len(dict_list)} items from ra centre site")

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

        return n_rows
    
    except Exception as e:
        conn.close()
        server.stop()
        raise(e)
    
if __name__ == "__main__":
    _ = main()