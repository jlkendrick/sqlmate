from .constants import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
from contextlib import contextmanager
from typing import Generator
from datetime import datetime
from mysql.connector import connect
from mysql.connector.abstracts import MySQLCursorAbstract
import pytz
from datetime import timedelta

# user_db = mysql.connector.connect(
#     host=DB_HOST,
#     user=DB_USER,
#     password=DB_PASSWORD,
#     database=DB_NAME
# )

user_db_config = {
	"host": DB_HOST,
	"user": DB_USER,
	"password": DB_PASSWORD,
	"database": DB_NAME
}

# sqlmate_db = mysql.connector.connect(
# 	host=DB_HOST,
# 	user=DB_USER,
# 	password=DB_PASSWORD,
# 	database="sqlmate"
# )

sqlmate_db_config = {
	"host": DB_HOST,
	"user": DB_USER,
	"password": DB_PASSWORD,
	"database": "sqlmate"
}

@contextmanager
def get_cursor(whose: str = "user") -> Generator[MySQLCursorAbstract, None, None]:
    db = (
        connect(**user_db_config) if whose == "user"
        else connect(**sqlmate_db_config)
    )
    cursor = db.cursor()
    try:
        yield cursor
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        cursor.close()
        db.close()


def get_timestamp() -> str:
	current_time_utc = datetime.now(pytz.utc) - timedelta(hours=4)
	formatted_time = current_time_utc.strftime("%Y-%m-%d %H:%M:%S")

	return formatted_time