"""
web_scraper.src.setup

This module provides the setup and configuration for the web scraping application.
It includes functions to load environment variables, retrieve database passwords,
and establish SSH tunnels and MySQL database connections.
"""

import os
from io import StringIO
import logging

import pytz
import mysql.connector
import paramiko
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

def db_connect():
    """
    configure database connection

    Returns:
        server: ssh server connection object
        conn: mysql db connection object
    """
    ssh_key = os.environ.get("JUMP_HOST_SSH_KEY")
    shh_key = ssh_key.replace(r"\n", "\n")
    pkey = paramiko.Ed25519Key.from_private_key(StringIO(shh_key))

    jump_host = os.environ.get("JUMP_HOST")
    jump_user = os.environ.get("JUMP_USER")
    rds_host = os.environ.get("DB_HOST")
    rds_port = int(os.environ.get("DB_PORT"))
    rds_user = os.environ.get("DB_USER")
    rds_password = os.environ.get("DB_PSWD")
    rds_db_name = os.environ.get("DB_NAME")
    local_port = int(os.environ.get("LOCAL_PORT"))

    server = None
    try:
        server = SSHTunnelForwarder(
            (jump_host, 22),
            ssh_username=jump_user,
            ssh_pkey=pkey,
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

def get_s3_bucket():
    """
    return the correct s3 bucket for prod and dev deployments
    """
    my_env = os.environ.get("ENV", "dev")
    if my_env == "prod":
        s3_bucket = "ra-center-raw-data-prod"
    else:
        s3_bucket = "ra-center-raw-data-dev"

    return s3_bucket
