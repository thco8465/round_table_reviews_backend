import psycopg2
from psycopg2 import sql
from datetime import datetime

# Establish a connection to your database
def get_db_connection():
    connection = psycopg2.connect(
        dbname='your_database_name',
        user='your_username',
        password='your_password',
        host='127.0.0.1',
        port='5432'
    )
    return connection

def insert_or_update_game(games):
    try:
        # Establish a database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create an array of game values for bulk insert/update
        values = [(game['name'], 
                   game['normalized_name'], 
                   game['cover'], 
                   game['description'], 
                   datetime.now(),  # Set created_at to current date
                   datetime.now())  # Set updated_at to current date
                  for game in games]

        # Create a SQL query with placeholders
        query = sql.SQL("""
            INSERT INTO games (name, normalized_name, cover, description, created_at, updated_at) 
            VALUES %s
            ON CONFLICT (name) 
            DO UPDATE
            SET 
                normalized_name = EXCLUDED.normalized_name,
                cover = EXCLUDED.cover,
                description = EXCLUDED.description,
                updated_at = EXCLUDED.updated_at
        """)

        # Execute the query
        psycopg2.extras.execute_values(cursor, query, values)
        conn.commit()
        print('Games inserted or updated successfully.')

    except Exception as error:
        print('Error inserting or updating games:', error)
        raise error  # Rethrow error after logging

    finally:
        cursor.close()
        conn.close()
