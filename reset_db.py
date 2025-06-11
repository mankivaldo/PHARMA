import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Connect to PostgreSQL server
conn = psycopg2.connect(
    dbname='postgres',
    user='postgres',
    password='23162428',
    host='localhost',
    port='5432'
)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor()

# Drop and recreate database
try:
    cur.execute('DROP DATABASE IF EXISTS PHARMA_NAPO')
    cur.execute('CREATE DATABASE PHARMA_NAPO')
    print("Database reset successfully")
except Exception as e:
    print(f"Error: {e}")
finally:
    cur.close()
    conn.close()
