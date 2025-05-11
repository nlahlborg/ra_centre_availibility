"""
web_scraper.src.setup

This module provides the setup and configuration for the preprosser
"""
import os
from io import StringIO
import logging

import pytz
import paramiko
from sshtunnel import SSHTunnelForwarder
import psycopg
import dotenv

logger = logging.getLogger(__name__)

RA_CENTRE_TZ = pytz.utc # timestamps from RA center website are in UTC
LOCAL_TZ = pytz.timezone('US/Pacific')
DISPLAY_TZ = pytz.timezone("America/Toronto")

ENV = os.environ.get("ENV", "dev")

def get_s3_bucket(override=False):
    """
    return the correct s3 bucket for prod and dev deployments
    """
    if override:
        s3_bucket = override
    else:
        my_env = os.environ.get("ENV", "dev")
        if my_env == "prod":
            s3_bucket = "ra-center-raw-data-prod"
        else:
            s3_bucket = "ra-center-raw-data-dev"
    return s3_bucket

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
        logger.debug(f"Successfully loaded environment variables from {filepath}")
        return True
    except FileNotFoundError:
        logger.error(f"Error: .env file not found at {filepath}")
        return False

def db_connect():
    """
    configure database connection

    Returns:
        server: ssh server connection object
        conn: PosgreSQL db connection object
    """
    server = None
    try:
        if ENV in ["prod", "lambda_stage"]:
            ssh_key = os.environ.get("JUMP_HOST_SSH_KEY", os.environ.get("EC2_SSH_KEY"))
            shh_key = ssh_key.replace(r"\n", "\n")
            pkey = paramiko.Ed25519Key.from_private_key(StringIO(shh_key))
            jump_host = os.environ.get("JUMP_HOST")
            jump_user = os.environ.get("JUMP_USER")

            rds_host = os.environ.get("DB_HOST_PROD")
            rds_port = int(os.environ.get("DB_PORT_PROD"))
            rds_user = os.environ.get("DB_USER_PROD")
            rds_password = os.environ.get("DB_PSWD_PROD")
            rds_db_name = os.environ.get("DB_NAME_PROD")
            local_port = int(os.environ.get("LOCAL_PORT"))

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

            logger.info("SSH tunnel established. Connecting to PosgreSQL database...")

            conn = psycopg.connect(
                host='127.0.0.1',
                port=server.local_bind_port,
                user=rds_user,
                password=rds_password,
                dbname=rds_db_name,
                connect_timeout=10,
            )

        else:
            rds_host = os.environ.get("DB_HOST_DEV")
            rds_port = int(os.environ.get("DB_PORT_DEV"))
            rds_user = os.environ.get("DB_USER_DEV")
            rds_password = os.environ.get("DB_PSWD_DEV")
            rds_db_name = os.environ.get("DB_NAME_DEV")

            conn = psycopg.connect(
                host=rds_host,
                port=rds_port,
                user=rds_user,
                password=rds_password,
                dbname=rds_db_name,
                connect_timeout=10,
            )

            server = None

        return server, conn

    except psycopg.Error as err:
        logger.error(f"Error connecting to PosgreSQL database: {err}")
        if server:
            server.stop()
        return None
    except Exception as e: # pylint: disable=broad-exception-caught
        logger.error(f"An unexpected error occurred: {e}")
        if server:
            server.stop()
        return None
