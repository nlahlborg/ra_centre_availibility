import sqlite3
import pandas as pd
import logging

logger = logging.getLogger("data_parser")
CONN = sqlite3.connect('.database\\ra_centre_availability.db')

def compare_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compare the new data with the existing data in the database.
    """

    # Get the existing data from the database
    existing_data = pd.read_sql("SELECT * FROM badminton_courts", CONN)

    # Check if the new data is already in the database
    if existing_data.empty:
        return df
    else:
        existing_data = existing_data.set_index(['facility_name', 'start_datetime', 'num_people'])
        df = df.set_index(['facility_name', 'start_datetime', 'num_people'])
        new_data = df.loc[df.index.difference(existing_data.index)].reset_index()
        return new_data

def prepare_transaction(df: pd.DataFrame) -> str:
    """
    Prepare the transaction string for the database.
    """
    new_data = compare_data(df)

    transation = "BEGIN TRANSACTION;\n"
    for index, row in new_data.iterrows():
        transation += f"""
        INSERT INTO badminton_courts (facility_name, start_datetime, end_datetime, num_people, has_reg_ended, inserted_datetime)
        VALUES ('{row['facility_name']}', '{row['start_datetime']}', '{row['end_datetime']}', {row['num_people']}, {row['has_reg_ended']}, '{row['inserted_datetime']}');
        """
    n_rows = new_data.shape[0]
    
    transation += "COMMIT;"
    return transation, n_rows

def save_data(transaction):
    """
    Save the data to the database.
    """
    try:
        CONN.executescript(transaction)
        CONN.commit()
        logger.info("Data saved to the database.")	
    except Exception as e:
        CONN.rollback()
        raise e