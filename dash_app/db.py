# db.py
import os
import pymysql  # or "mysql-connector-python"
from dotenv import load_dotenv

load_dotenv()  # load .env variables if needed

def get_db_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),      # same env variables
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT", 3306)),
        cursorclass=pymysql.cursors.DictCursor
    )