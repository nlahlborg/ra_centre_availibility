import pandas as pd
import logging

logger = logging.getLogger("data_parser")

def compare_data(df: pd.DataFrame, conn) -> pd.DataFrame:
    """
    Compare the new data with the existing data in the database.
    """

    # construct the query
    query = f"""
        SELECT facility_name, start_datetime, num_people 
        FROM badminton_courts
        WHERE start_datetime >= \"{df['start_datetime'].min()}\"
        LIMIT 1000
        """
    existing_data = pd.read_sql(query, conn)

    # Check if the new data is already in the database
    if existing_data.empty:
        return df
    else:
        existing_data = existing_data.set_index(['facility_name', 'start_datetime', 'num_people'])
        df = df.set_index(['facility_name', 'start_datetime', 'num_people'])
        new_data = df.loc[df.index.difference(existing_data.index)].reset_index()
        return new_data

def prepare_transaction(df: pd.DataFrame, conn: str) -> str:
    """
    depricated
    Prepare the sqlite3 transaction string for the database.
    """
    new_data = compare_data(df, conn)
    
    transation = "BEGIN TRANSACTION;\n"
    for index, row in new_data.iterrows():
        transation += f"""
        INSERT INTO badminton_courts (facility_name, start_datetime, end_datetime, num_people, has_reg_ended, inserted_datetime)
        VALUES ('{row['facility_name']}', '{row['start_datetime']}', '{row['end_datetime']}', {row['num_people']}, {row['has_reg_ended']}, '{row['inserted_datetime']}');
        """
    n_rows = new_data.shape[0]
    
    transation += "COMMIT;"
    return transation, n_rows

def save_data(transaction: str, conn: str):
    """
    depricated
    Save the data to the sqlite database.
    """
    try:
        conn.executescript(transaction)
        conn.commit()
        logger.info("Data saved to the database.")	
    except Exception as e:
        conn.rollback()
        raise e