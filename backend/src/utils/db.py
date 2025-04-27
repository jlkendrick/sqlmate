from .constants import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
from contextlib import contextmanager
from datetime import datetime
import mysql.connector
import pytz

db = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)

@contextmanager
def get_cursor():
	cursor = db.cursor()
	try:
		yield cursor
		db.commit()
	except Exception as e:
		db.rollback()
		raise e
	finally:
		cursor.close()

def get_timestamp() -> str:
	current_time_utc = datetime.now(pytz.utc)
	formatted_time = current_time_utc.strftime("%Y-%m-%d %H:%M:%S")

	return formatted_time