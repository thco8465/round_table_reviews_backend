import os
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create a connection pool
try:
    db_pool = pool.SimpleConnectionPool(
        1,  # Minimum number of connections
        10,  # Maximum number of connections
        user=os.getenv('DATABASE_USERNAME'),
        host=os.getenv('DATABASE_HOST'),
        database=os.getenv('DATABASE_NAME'),
        password=os.getenv('DATABASE_PASSWORD'),
        port='5432'
    )

    if db_pool:
        print("Connection pool created successfully.")

except Exception as e:
    print("Error creating connection pool:", e)

def get_connection():
    """Get a connection from the pool."""
    try:
        connection = db_pool.getconn()
        if connection:
            print("Successfully obtained a connection from the pool.")
            return connection
    except Exception as e:
        print("Error obtaining connection:", e)

def release_connection(connection):
    """Release a connection back to the pool."""
    try:
        db_pool.putconn(connection)
        print("Connection released back to the pool.")
    except Exception as e:
        print("Error releasing connection:", e)
