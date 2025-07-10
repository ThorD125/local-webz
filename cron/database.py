import os
import sys
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv(dotenv_path='.env')

# Get credentials
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
database = os.getenv("POSTGRES_DB")
host = "db"  # Name of the Postgres service in docker-compose

# Connect to the database

def get_db_data():
    try:
        conn = psycopg2.connect(
            dbname=database,
            user=user,
            password=password,
            host=host
        )
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM url;")
        rows = cursor.fetchall()

        data = [
            {
                "url": row[1],
                "css": row[2],
                "js": row[3],
                "frequency": row[4]
            }
            for row in rows
        ]

        cursor.close()
        conn.close()

        return data

    except:
        sys.exit(1)

if __name__ == "__main__":
    print(get_db_data())
    print("[✓] All done.")
