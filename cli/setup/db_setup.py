"""
Database setup utilities for SQLMate CLI.

This module contains functions for initializing database tables
and other database setup tasks required for SQLMate to function properly.
"""
from .sql.database import (
    CREATE_SQLMATE_DATABASE
)
from .sql.tables import (
    CREATE_USERS_TABLE,
    CREATE_USER_TABLES_TABLE,
    CREATE_TABLES_TO_DROP_TABLE
)
from .sql.triggers import (
    CREATE_BEFORE_DELETE_ON_USER_TABLES_TRIG
)
from .sql.procedures import (
    CREATE_SAVE_USER_TABLE_PROC,
    CREATE_PROCESS_TABLE_TO_DROP_PROC
)
from typing import Optional
import time
import mysql.connector
from mysql.connector.abstracts import MySQLConnectionAbstract
from mysql.connector.pooling import PooledMySQLConnection

def connect_with_retry(credentials: dict, max_retries: int=5, delay: int=2) -> Optional[MySQLConnectionAbstract | PooledMySQLConnection]:
    """
    Attempt to connect to the MySQL server with retries.
    
    Args:
        credentials (dict): Database credentials
        max_retries (int): Maximum number of connection attempts
        delay (int): Seconds to wait between retries
        
    Returns:
        connection: MySQL connection object or None if connection failed
    """
    for attempt in range(max_retries):
        try:
            print(f"Attempting to connect to database (attempt {attempt + 1}/{max_retries})...")
            temp_connection = mysql.connector.connect(
                host=credentials["DB_HOST"],
                user=credentials["DB_USER"],
                password=credentials["DB_PASSWORD"]
            )
            print("✅ Database server connection successful!")

            # Check if the database exists
            cursor = temp_connection.cursor()
            cursor.execute(f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{credentials['DB_NAME']}'")
            if not cursor.fetchone():
                print(f"❌ Database '{credentials['DB_NAME']}' does not exist. Please create it first.")
                temp_connection.close()
                return None
            print(f"✅ Database '{credentials['DB_NAME']}' found.")

            # Create the 'sqlmate' database if it doesn't exist
            cursor.execute(CREATE_SQLMATE_DATABASE)
            cursor.close()
            temp_connection.commit()
            temp_connection.close()

            # Create a new connection to the 'sqlmate' database
            connection = mysql.connector.connect(
                host=credentials["DB_HOST"],
                user=credentials["DB_USER"],
                password=credentials["DB_PASSWORD"],
                database="sqlmate"
            )

            return connection
        
        except mysql.connector.Error as err:
            print(f"❌ Connection failed: {err}")
            if attempt < max_retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("❌ Maximum retry attempts reached. Could not connect to server.")
                return None
    
    return None

def create_tables(connection: MySQLConnectionAbstract | PooledMySQLConnection) -> bool:
    """
    Create the necessary tables for SQLMate.
    
    Args:
        connection: MySQL connection object
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        cursor = connection.cursor()
        
        print("🔧 Creating tables...")
        queries = [
            CREATE_USERS_TABLE,
            CREATE_USER_TABLES_TABLE,
            CREATE_TABLES_TO_DROP_TABLE
        ]
        
        for table_query in queries:
            cursor.execute(table_query)
        
        connection.commit()
        cursor.close()
        print("✅ Database tables created successfully")
        return True
        
    except mysql.connector.Error as err:
        print(f"❌ Error creating tables: {err}")
        print("Make sure you have the necessary permissions to create databases and tables in your DBMS.")
        return False
    
def create_triggers_and_procedures(connection: MySQLConnectionAbstract | PooledMySQLConnection) -> bool:
    """
    Create necessary triggers and stored procedures for SQLMate.
    
    Args:
        connection: MySQL connection object
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        cursor = connection.cursor()
        
        print("🔧 Creating triggers and stored procedures...")
        queries = [
            CREATE_BEFORE_DELETE_ON_USER_TABLES_TRIG,
            CREATE_SAVE_USER_TABLE_PROC,
            CREATE_PROCESS_TABLE_TO_DROP_PROC
        ]

        for query in queries:
            cursor.execute(query)

        # Commit the changes to the database
        connection.commit()
        cursor.close()
        print("✅ Triggers and stored procedures created successfully")
        return True
        
    except mysql.connector.Error as err:
        print(f"❌ Error creating triggers or procedures: {err}")
        return False

def initialize_database(credentials: dict) -> bool:
    """
    Main function to validate and initialize the database for SQLMate.
    Currently only supports MySQL, will add backend support for other databases later.
    
    Args:
        credentials (dict): Database credentials
        
    Returns:
        bool: True if successful, False otherwise
    """
    print("\n🔧 Initializing database...")
    
    # Connect to database
    connection = connect_with_retry(credentials)
    if not connection:
        return False
    
    # Create tables
    if not create_tables(connection):
        connection.close()
        return False
    
    # Create triggers and procedures
    if not create_triggers_and_procedures(connection):
        connection.close()
        return False
    
    connection.close()
    print("✅ Database initialization completed successfully")
    return True
