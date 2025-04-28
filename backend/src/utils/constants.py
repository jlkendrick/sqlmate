from dotenv import load_dotenv
import os

load_dotenv('/app/secrets.env')

# Port
PORT = int(os.getenv("PORT", 8080))

# JWT configuration
SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

# DB configuration
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

