import dotenv
import os
import pytz
import mysql.connector

DB_TZ = pytz.UTC
RA_CENTRE_TZ = pytz.timezone('US/Pacific') # timestamps from RA center website are in pacific time
INDEX1 = ["facility_name", "start_datetime"]
INDEX2 = ["facility_name", "start_datetime", "num_people"]
ALL_COLS = ["facility_name", "start_datetime", "end_datetime", "num_people", "has_reg_ended", "inserted_datetime"]


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

def db_connect():
    try:
        conn = mysql.connector.connect(
            host=os.environ.get("DB_HOST"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PSWD"),
            database=os.environ.get("DB_NAME")
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL database: {err}")
        return None
