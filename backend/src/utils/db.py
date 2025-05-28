from .constants import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
from contextlib import contextmanager
from typing import Generator, Any
from datetime import datetime
import mysql.connector
from mysql.connector.abstracts import MySQLCursorAbstract
import pytz

user_db = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)

sqlmate_db = mysql.connector.connect(
	host=DB_HOST,
	user=DB_USER,
	password=DB_PASSWORD,
	database="sqlmate"
)

@contextmanager
def get_cursor(whose: str = "user") -> Generator[MySQLCursorAbstract, Any, Any]:
	cursor = user_db.cursor() if whose == "user" else sqlmate_db.cursor()
	try:
		yield cursor
		if whose == "user":
			user_db.commit()
		else:
			sqlmate_db.commit()
	except Exception as e:
		if whose == "user":
			user_db.rollback()
		else:
			sqlmate_db.rollback()
		raise e
	finally:
		cursor.close()

def get_timestamp() -> str:
	current_time_utc = datetime.now(pytz.utc)
	formatted_time = current_time_utc.strftime("%Y-%m-%d %H:%M:%S")

	return formatted_time