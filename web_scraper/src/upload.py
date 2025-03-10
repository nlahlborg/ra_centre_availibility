from datetime import datetime
from typing import List, Dict, Any
import logging
import mysql.connector 

from src.setup import TABLE_NAME, RA_CENTRE_TZ, ALL_COLS, INDEX2 as primary_key
MIN_START_DATETIME = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).astimezone(RA_CENTRE_TZ).strftime("%Y-%m-%d %H:%M:%S")

DataObject = List[Dict[str, Any]]

logger = logging.getLogger("data_parser")

def compare_data(data: DataObject, existing_data: DataObject) -> DataObject:
    if not existing_data:
        return data
    else:
        # Create set of existing tuples
        existing_indexes = set(tuple([row[col] for col in primary_key]) for row in existing_data)
        input_indexes = set(tuple([row[col] for col in primary_key]) for row in data)

        new_rows_indexes = list(input_indexes.difference(existing_indexes))

        # Find new rows in the original data set
        new_data = []     
        data_index = [tuple([row[col] for col in primary_key]) for row in data]   
        for idx in new_rows_indexes:
            new_data.append(data[data_index.index(idx)])

        return new_data

def get_existing_data(min_start_datetime: str, 
    conn: mysql.connector.connection.MySQLConnection,
    table_name: str=TABLE_NAME) -> DataObject:
    # construct the query
    query = f"""
        SELECT {', '.join([col for col in ALL_COLS])}
        FROM {table_name}
        WHERE start_datetime >= \"{min_start_datetime}\"
        """
    
    #read from db
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    existing_data = cursor.fetchall()
    cursor.close()
    return existing_data

def get_only_new_data(data: DataObject, 
    conn: mysql.connector.connection.MySQLConnection,
    table_name=TABLE_NAME) -> DataObject:
    """
    Compare the new data with the existing data in the database.
    """
    existing_data = get_existing_data(MIN_START_DATETIME, conn, table_name)

    # Check if the new data is already in the database
    new_data = compare_data(data, existing_data)

    return new_data
    
def prepare_transaction(data: DataObject, table_name: str=TABLE_NAME) -> str:
    """
    Prepare the mysql transaction string for the database.
    """
    if not data:
        return ""
    
    columns = ALL_COLS
    values = []
    for row in data:
        row_values = []
        for col in columns:
            value = row.get(col)
            if isinstance(value, str):
                row_values.append(f"'{value}'")
            elif value is None:
                row_values.append('NULL')
            elif isinstance(value, datetime):
                row_values.append(f"'{value.strftime('%Y-%m-%d %H:%M:%S')}'")
            else:
                row_values.append(str(value))
        values.append(f"({', '.join(row_values)})")

    columns_str = ", ".join(columns)
    values_str = ", ".join(values)
    sql = f"INSERT INTO {table_name} ({columns_str}) VALUES {values_str};"
    return sql
    
def save_data(sql: str, conn: mysql.connector.connection.MySQLConnection):
    """
    depricated
    Save the data to the sqlite database.
    """
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()  # Important: Commit the changes
        cursor.close()
    except Exception as e:
        logger.error("failed to execute SQL inert")
        raise e