import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def reset_database():
    # Connect to PostgreSQL server
    conn = psycopg2.connect(
        dbname='PHARMA_NAPO',
        user='postgres',
        password='23162428',
        host='localhost',
        port='5432'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    # Get list of all tables
    cur.execute("""
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public'
    """)
    tables = cur.fetchall()

    # Drop all tables
    for table in tables:
        try:
            cur.execute(f'DROP TABLE IF EXISTS "{table[0]}" CASCADE')
            print(f"Dropped table: {table[0]}")
        except Exception as e:
            print(f"Error dropping {table[0]}: {e}")

    cur.close()
    conn.close()

if __name__ == "__main__":
    reset_database()
