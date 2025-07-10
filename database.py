import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv(dotenv_path='.env')

# Get credentials
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
database = os.getenv("POSTGRES_DB")
host = "db"  # Name of the Postgres service in docker-compose
host = "192.168.1.100"  # Name of the Postgres service in docker-compose

# Connect to the database
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

    print("Users:")
    for row in rows:
        print(row)

    cursor.close()
    conn.close()

except Exception as e:
    print(f"[ERROR] {e}")
