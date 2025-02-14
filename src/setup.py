import dotenv
import os
import pytz

TZ = pytz.UTC

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
    return f'mysql+mysqlconnector://{os.environ.get("DB_USER")}:{os.environ.get("DB_PSWD")}@{os.environ.get("DB_HOST")}/{os.environ.get("DB_NAME")}'