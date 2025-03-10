"""
web_scraper.src.setup

This module provides the setup and configuration for the web scraping application.
It includes functions to load environment variables, retrieve database passwords,
and establish SSH tunnels and MySQL database connections.
"""

import os
from pathlib import Path
import logging

import pytz
import mysql.connector
from sshtunnel import SSHTunnelForwarder
import dotenv

logger = logging.getLogger("setup")

LOCAL_TZ = pytz.timezone('US/Pacific')
DB_TZ = pytz.timezone('UTC')
TABLE_NAME = "sports_facilities"
RA_CENTRE_TZ = pytz.timezone('US/Eastern') # timestamps from RA center website are in eastern time
INDEX1 = ["slot_id", "inserted_datetime"] #primary key
INDEX2 = ["slot_id", "num_people"] #alternate key
ALL_COLS = [
    "slot_id", 
    "display_name", 
    "facility_name", 
    "facility_type", 
    "start_datetime", 
    "end_datetime", 
    "num_people", 
    "has_reg_ended", 
    "inserted_datetime"
]

def load_env_file(filepath):
    """Loads environment variables from a .env file.

    Args:
        filepath: The path to the .env file.  Handles both forward and backslashes.
    
    Returns:
        True if the .env file was loaded successfully, False otherwise.
        Prints informative messages to the console if there are errors.
    """
    try:
        # override=False to not overwrite existing env vars
        dotenv.load_dotenv(dotenv_path=filepath, verbose=True, override=False)
        logger.info(f"Successfully loaded environment variables from {filepath}")
        return True
    except FileNotFoundError:
        logger.error(f"Error: .env file not found at {filepath}")
        return False

def get_db_password(fpath):
    """
    read the db_password
    """
    with open(fpath, 'r', encoding="UTF-8") as file:
        db_password = file.read().strip()
    return db_password

def db_connect():
    """
    configure database connection

    Returns:
        server: ssh server connection object
        conn: mysql db connection object
    """
    jump_host = os.environ.get("JUMP_HOST")
    jump_user = os.environ.get("JUMP_USER")
    jump_ssh_key_path = str(Path(__file__).parent.parent) + os.environ.get("SSH_KEY_PATH")
    rds_host = os.environ.get("DB_HOST")
    rds_port = int(os.environ.get("DB_PORT"))
    rds_user = os.environ.get("DB_USER")
    rds_password = get_db_password(str(Path(__file__).parent.parent) \
        + os.environ.get("DB_PSWD_PATH"))
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
    except Exception as e: # pylint: disable=broad-exception-caught
        logger.error(f"An unexpected error occurred: {e}")
        if server:
            server.stop()
        return None
