import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE = {
    'host': os.getenv('RM_DB_HOST'),
    'user': os.getenv('RM_DB_USER'),
    'password': os.getenv('RM_DB_PASS'),
    'database': os.getenv('RM_DB_NAME')
}

def test_db_connection():
    print("Environment Variables:")
    print(f"RM_DB_HOST: {DATABASE['host']}")
    print(f"RM_DB_USER: {DATABASE['user']}")
    print(f"RM_DB_PASS: {DATABASE['password']}")
    print(f"RM_DB_NAME: {DATABASE['database']}")

    try:
        print("Connecting to the database...")
        conn = pymysql.connect(
            host=DATABASE['host'],
            port=3306,
            user=DATABASE['user'],
            password=DATABASE['password'],
            database=DATABASE['database'],
            cursorclass=pymysql.cursors.DictCursor
        )
        print("Connection successful!")
        conn.close()
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"General Error: {e}")

if __name__ == "__main__":
    test_db_connection()
