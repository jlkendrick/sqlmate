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
from typing import Optional, Dict, List, Any, Tuple
from collections import defaultdict
import mysql.connector
from mysql.connector.abstracts import MySQLConnectionAbstract
from mysql.connector.pooling import PooledMySQLConnection
import time
import os
import json

def connect_with_retry(credentials: Dict[str, str],
        max_retries: int=5,
        delay: int=2,
        from_init: bool = True)  \
    -> Optional[MySQLConnectionAbstract | PooledMySQLConnection]:
    """
    Attempt to connect to the MySQL server with retries.
    
    Args:
        credentials (dict): Database credentials
        max_retries (int): Maximum number of connection attempts
        delay (int): Seconds to wait between retries
        from_init (bool): Flag to indicate if called from initialization
        
    Returns:
        connection: MySQL connection object or None if connection failed
    """
    for attempt in range(max_retries):
        try:
            print(f"Attempting to connect to database (attempt {attempt + 1}/{max_retries})...")
            connection = mysql.connector.connect(
                host=credentials["DB_HOST"],
                user=credentials["DB_USER"],
                password=credentials["DB_PASSWORD"]
            )
            print("✅ Database server connection successful!")

            # Check if the database exists
            cursor = connection.cursor()
            cursor.execute(f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{credentials['DB_NAME']}'")
            if not cursor.fetchone():
                print(f"❌ Database '{credentials['DB_NAME']}' does not exist. Please create it first.")
                connection.close()
                return None
            if from_init:
                print(f"✅ Database '{credentials['DB_NAME']}' found.")

            # Create the 'sqlmate' database if it doesn't exist
            cursor = connection.cursor()
            cursor.execute(CREATE_SQLMATE_DATABASE)
            cursor.close()
            connection.commit()

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

def fetch_metadata(connection: MySQLConnectionAbstract | PooledMySQLConnection, db_name: str) -> Tuple[bool, Dict[str, Any]]:
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME NOT LIKE 'u_%'
                ORDER BY TABLE_NAME, ORDINAL_POSITION;
                """, (db_name,)
            )
            rows: List[Any] = cursor.fetchall()
            metadata = defaultdict(list)
            for table, column, data_type in rows:
                metadata[table].append({
                    "column": column,
                    "data_type": data_type
                })
        return True, metadata
    except mysql.connector.Error as err:
        print(f"❌ Error fetching schema: {err}")
        return False, {}
    

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
    
def create_triggers_and_procedures(connection: MySQLConnectionAbstract | PooledMySQLConnection, db_name: str) -> bool:
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
            CREATE_SAVE_USER_TABLE_PROC.format(
                db_name=db_name
            ),
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
    
    # Generate JSON schema file for frontend use
    success, metadata = fetch_metadata(connection, credentials["DB_NAME"])
    if not success:
        connection.close()
        return False

    # Prompt user to select tables for schema
    filtered_metadata = prompt_user_for_tables(metadata)
    
    # Generate schema in required format
    schema = generate_db_schema_json(filtered_metadata)
    
    # Write schema to file
    try:
        # Use home directory to store the schema
        home_dir = os.path.expanduser("~")
        sqlmate_dir = os.path.join(home_dir, '.sqlmate')
        schema_path = os.path.join(sqlmate_dir, 'db_schema.json')
        
        # Ensure the directory exists
        os.makedirs(sqlmate_dir, exist_ok=True)
        
        # Write the schema to file
        with open(schema_path, 'w') as f:
            json.dump(schema, f, indent=2)
        
        print(f"✅ Schema file generated at {schema_path}")
        
        # Try to copy to frontend directory if it exists
        copy_schema_to_frontend(schema_path)
    except Exception as e:
        print(f"❌ Error writing schema file: {e}")
        connection.close()
        return False

    # Create tables
    if not create_tables(connection):
        connection.close()
        return False
    
    # Create triggers and procedures
    if not create_triggers_and_procedures(connection, credentials["DB_NAME"]):
        connection.close()
        return False

    connection.close()
    
    print("✅ Database initialization completed successfully")
    return True

def prompt_user_for_tables(metadata: Dict[str, List[Dict[str, str]]]) -> Dict[str, List[Dict[str, str]]]:
    """
    Prompt the user for each table, asking if they want to keep it in the schema.
    
    Args:
        metadata (Dict[str, List[Dict[str, str]]]): Dictionary of tables and their columns
        
    Returns:
        Dict[str, List[Dict[str, str]]]: Filtered metadata with only the tables the user wants to keep
    """
    filtered_metadata = {}
    
    print("\n📋 Select tables to include in your schema:")
    
    # Get list of tables
    tables = list(metadata.keys())
    
    # Skip if there are no tables
    if not tables:
        print("❌ No tables found in the database.")
        return filtered_metadata
    
    # Ask for each table
    for table in tables:
        print(f"\nTable: {table} ({len(metadata[table])} columns)")
        print("Columns:")
        for column_info in metadata[table][:5]:  # Show only first 5 columns as preview
            print(f"  - {column_info['column']} ({column_info['data_type']})")
        
        if len(metadata[table]) > 5:
            print(f"  ... and {len(metadata[table]) - 5} more columns")
        
        keep_table = input(f"Include '{table}' in schema? (y/n): ").lower().strip()
        
        if keep_table == 'y' or keep_table == 'yes':
            filtered_metadata[table] = metadata[table]
            print(f"✅ Added '{table}' to schema")
        else:
            print(f"❌ Excluded '{table}' from schema")
    
    if not filtered_metadata:
        print("\n⚠️ Warning: No tables selected for schema.")
        confirm = input("Continue without any tables? (y/n): ").lower().strip()
        if confirm != 'y' and confirm != 'yes':
            print("Let's try again...")
            return prompt_user_for_tables(metadata)
    
    return filtered_metadata

def generate_db_schema_json(metadata: Dict[str, List[Dict[str, str]]]) -> List[Dict[str, Any]]:
    """
    Convert metadata to the format required for db_schema.json
    
    Args:
        metadata (Dict[str, List[Dict[str, str]]]): Dictionary of tables and their columns
        
    Returns:
        List[Dict[str, Any]]: List of tables with their columns in the required format
    """
    schema = []
    
    for table_name, columns in metadata.items():
        table_schema = {
            "table": table_name,
            "columns": []
        }
        
        for column_info in columns:
            column_name = column_info["column"]
            data_type = column_info["data_type"].upper()
            
            # Map MySQL data types to more general SQL types if needed
            if data_type == "INT":
                type_name = "INT"
            elif data_type in ["VARCHAR", "CHAR", "TEXT"]:
                type_name = f"{data_type}(255)"  # Default size
            elif data_type in ["DECIMAL", "NUMERIC"]:
                type_name = "DECIMAL(10,2)"  # Default precision
            elif data_type == "DATETIME" or data_type == "TIMESTAMP":
                type_name = data_type
            elif data_type == "DATE":
                type_name = "DATE"
            elif data_type == "BOOLEAN" or data_type == "TINYINT":
                type_name = "BOOLEAN"
            else:
                type_name = data_type
            
            table_schema["columns"].append({
                "name": column_name,
                "type": type_name
            })
        
        schema.append(table_schema)
    
    return schema

def copy_schema_to_frontend(schema_path: str) -> bool:
    """
    Copy the schema file to the frontend public directory if needed.
    
    Args:
        schema_path (str): Path to the schema file
        
    Returns:
        bool: True if successful or not needed, False otherwise
    """
    try:
        # Check if we're running from the SQLMate project directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
        frontend_public = os.path.join(project_root, 'frontend', 'public')
        
        # If frontend directory exists, copy the schema there too
        if os.path.exists(frontend_public):
            frontend_schema_path = os.path.join(frontend_public, 'db_schema.json')
            
            # Copy the schema file
            with open(schema_path, 'r') as src_file:
                schema_data = json.load(src_file)
                
            with open(frontend_schema_path, 'w') as dest_file:
                json.dump(schema_data, dest_file, indent=2)
                
            print(f"✅ Schema file also copied to {frontend_schema_path}")
        
        return True
    except Exception as e:
        print(f"⚠️ Note: Could not copy schema to frontend directory: {e}")
        return True  # Not a fatal error, just a warning
