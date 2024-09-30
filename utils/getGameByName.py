import psycopg2
from flask import current_app

def get_game_by_normalized_name(normalized_name):
    try:
        # Get a connection from the application context
        with current_app.app_context():
            connection = psycopg2.connect(
                dbname=current_app.config['DATABASE_NAME'],
                user=current_app.config['DATABASE_USER'],
                password=current_app.config['DATABASE_PASSWORD'],
                host=current_app.config['DATABASE_HOST']
            )
            cursor = connection.cursor()
            cursor.execute(
                "SELECT * FROM games WHERE normalized_name = %s",
                (normalized_name,)
            )
            game = cursor.fetchone()  # Fetch the first match
            
            # Close the cursor and connection
            cursor.close()
            connection.close()

            return game  # Return the game data

    except Exception as error:
        print('Error fetching game by normalized name:', error)
        return None  # Return None in case of an error
