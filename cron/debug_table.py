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

def get_db_tables():
    try:
        conn = psycopg2.connect(
            dbname=database,
            user=user,
            password=password,
            host=host
        )
        cursor = conn.cursor()
        cursor.execute("""SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_type = 'BASE TABLE' AND table_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY table_schema, table_name;
""")
        rows = cursor.fetchall()

        print(rows)

        cursor.close()
        conn.close()

    except Exception as e:
        print(e)
        sys.exit(1)

if __name__ == "__main__":
    print(get_db_tables())
    print("[✓] All done.")
