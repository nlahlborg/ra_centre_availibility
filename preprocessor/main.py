from pathlib import Path
import logging
from src.setup import db_connect, load_env_file
from src.upload import load_data

logger = logging.getLogger("preprocessor.main")
logging.basicConfig(level=logging.INFO)

from pprint import pprint

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
    return retvar

if __name__ == "__main__":
    ids = main(True)
