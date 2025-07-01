from src.utils.constants import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
from contextlib import contextmanager
from typing import Generator, Any
from datetime import datetime
from mysql.connector import connect
from mysql.connector.abstracts import MySQLCursorAbstract
import pytz
from datetime import timedelta
from abc import ABC, abstractmethod

class DBInterface(ABC):
    @abstractmethod
    def connect(self) -> Any:
        pass

    @abstractmethod
    def get_cursor(self) -> Any:
        pass

    @abstractmethod
    def db_exists(self, db_name: str) -> bool:
        pass

    @abstractmethod
    def create_db(self, db_name: str) -> bool:
        pass

    @abstractmethod
    def fetch_metadata(self, db_name: str) -> dict:
        pass

    @abstractmethod
    def create_tables(self) -> bool:
        pass

    @abstractmethod
    def create_triggers_and_procedures(self, db_name: str) -> bool:
        pass

    @abstractmethod
    def close(self) -> None:
        pass


user_db_config = {
	"host": DB_HOST,
	"user": DB_USER,
	"password": DB_PASSWORD,
	"database": DB_NAME
}

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