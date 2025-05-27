"""
Database setup utilities for SQLMate CLI.

This module contains functions for initializing database tables
and other database setup tasks required for SQLMate to function properly.
"""

from typing import Optional
import mysql.connector
import time
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
            cursor.close()
            temp_connection.close()
            print(f"✅ Database '{credentials['DB_NAME']}' found.")

            # Get the actual connection to the specified database
            connection = mysql.connector.connect(
                host=credentials["DB_HOST"],
                user=credentials["DB_USER"],
                password=credentials["DB_PASSWORD"],
                database=credentials["DB_NAME"]
            )
            print("✅ Connected to the specified database successfully!")

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
        
        print("🔧 Creating database tables...")
        tables = [
            """
            CREATE DATABASE IF NOT EXISTS sqlmate
            """,
            """
            CREATE TABLE IF NOT EXISTS sqlmate.users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(100) NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS sqlmate.user_tables (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                table_name VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        ]
        
        for table_query in tables:
            cursor.execute(table_query)
        
        connection.commit()
        cursor.close()
        print("✅ Database tables created successfully")
        return True
        
    except mysql.connector.Error as err:
        print(f"❌ Error creating tables: {err}")
        print("Make sure you have the necessary permissions to create databases and tables in your DBMS.")
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
    
    connection.close()
    print("✅ Database initialization completed successfully")
    return True
