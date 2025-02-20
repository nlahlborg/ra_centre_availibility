import os
import pytz
from pathlib import Path
import mysql.connector
from sshtunnel import SSHTunnelForwarder
import logging
import dotenv

logger = logging.getLogger("setup")

DB_TZ = pytz.UTC
RA_CENTRE_TZ = pytz.timezone('US/Eastern') # timestamps from RA center website are in eastern time
INDEX1 = ["slot_id", "inserted_datetime"] #primary key
INDEX2 = ["slot_id", "num_people"] #alternate key
ALL_COLS = ["slot_id", "display_name", "code", "facility_name", "start_datetime", "end_datetime", "num_people", "has_reg_ended", "inserted_datetime"]

def load_env_file(filepath):
    """Loads environment variables from a .env file.

    Args:
        filepath: The path to the .env file.  Handles both forward and backslashes.
    
    Returns:
        True if the .env file was loaded successfully, False otherwise.
        Prints informative messages to the console if there are errors.
    """
    try:
        dotenv.load_dotenv(dotenv_path=filepath, verbose=True, override=False) # override=False to not overwrite existing env vars
        print(f"Successfully loaded environment variables from {filepath}")
        return True
    except FileNotFoundError:
        print(f"Error: .env file not found at {filepath}")
        return False
    except Exception as e: # Catch any other exceptions
        print(f"An error occurred while loading .env: {e}")
        return False
       
def get_mysql_connect_string():
    """
    deprecated
    """
    return f'mysql+mysqlconnector://{os.environ.get("DB_USER")}:{os.environ.get("DB_PSWD")}@{os.environ.get("DB_HOST")}/{os.environ.get("DB_NAME")}'

def get_db_password(fpath):
    print(f"*******************{fpath}")
    with open(fpath, 'r') as file:
        db_password = file.read().strip()
    return db_password

def db_connect():
    # Configuration
    jump_host = os.environ.get("JUMP_HOST")
    jump_user = os.environ.get("JUMP_USER")
    jump_ssh_key_path = str(Path(__file__).parent.parent) + os.environ.get("SSH_KEY_PATH")
    rds_host = os.environ.get("DB_HOST")
    rds_port = int(os.environ.get("DB_PORT"))
    rds_user = os.environ.get("DB_USER")
    rds_password = get_db_password(str(Path(__file__).parent.parent) + os.environ.get("DB_PSWD_PATH"))
    rds_db_name = os.environ.get("DB_NAME")
    local_port = int(os.environ.get("LOCAL_PORT"))
    
    server = None
    try:
        server = SSHTunnelForwarder(
            (jump_host, 22),
            ssh_username=jump_user,
            ssh_private_key=jump_ssh_key_path,
            remote_bind_address=(rds_host, rds_port),
            local_bind_address=('127.0.0.1', local_port),
            set_keepalive=30
        )
        logger.info("Credentials entered, preparing to start SSH")

        server.start()

        logger.info("SSH tunnel established. Connecting to MySQL database...")

        conn = mysql.connector.connect(
            host='127.0.0.1',
            port=server.local_bind_port,
            user=rds_user,
            password=rds_password,
            database=rds_db_name,
            connection_timeout=10,
            use_pure=True
        )

        return server, conn
    except mysql.connector.Error as err:
        logger.error(f"Error connecting to MySQL database: {err}")
        if server:
            server.stop()
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        if server:
            server.stop()
        return None