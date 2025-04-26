import os
from sqlalchemy import create_engine

DB_HOST = "localhost"
DB_PORT = 33062
DB_USER = "admin"
DB_PASSWORD = os.environ.get("DB_PSWD")
DB_NAME = "ra_centre_db2"

DATABASE_URI = f"mysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def db_connect(db_uri=DATABASE_URI):
    """
    configure database connection

    Returns:
        engine
    """
    return create_engine(DATABASE_URI)