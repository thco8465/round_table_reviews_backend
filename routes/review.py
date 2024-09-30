from flask import Flask, Blueprint, request, jsonify
from models import db, Review, ReviewInfo, Game  # Import your models
from datetime import datetime
from db import get_connection, release_connection
from psycopg2 import sql

review_bp = Blueprint('review', __name__)


# POST route to add a review
@review_bp.route('/review', methods=['POST'])
def add_review():
    data = request.json
    game_id = int(data.get('gameId'))
    game_name = data.get('game_name')
    user_id = data.get('userId')
    review = data.get('review')
    time_spent = data.get('timeSpent')
    rating = data.get('rating')
    date = data.get('date')

    # Validate required fields and their types
    if not all([isinstance(game_id, int), isinstance(game_name, str), isinstance(user_id, int), 
                isinstance(review, str), isinstance(time_spent, int), isinstance(rating, (int, float)), 
                isinstance(date, str)]):
        print('Invalid input data:', data)
        return jsonify({'error': 'Invalid input data'}), 400

    # Validate rating
    if rating < 1 or rating > 10:
        print('Invalid rating:', rating)
        return jsonify({'error': 'Rating must be between 1 and 10'}), 400

    # Convert and validate date
    try:
        parsed_date = datetime.fromisoformat(date)  # Expecting ISO format
    except ValueError:
        print('Invalid date format:', date)
        return jsonify({'error': 'Invalid date format'}), 400

    # Convert game_id and time_spent to integers
    game_id_int = int(game_id)
    time_spent_int = int(time_spent)

    conn = None
    cursor = None
    try:
        conn = get_connection()  # Obtain connection from the pool
        cursor = conn.cursor()
        
        # SQL query to insert the review
        insert_query = sql.SQL("""
            INSERT INTO reviews (game_id, game_name, user_id, review, time_spent, rating, date)
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;
        """)

        # Execute the insert query
        cursor.execute(insert_query, (game_id_int, game_name, user_id, review, time_spent_int, rating, parsed_date))
        new_review_id = cursor.fetchone()[0]  # Get the ID of the newly inserted review

        # Commit the transaction
        conn.commit()

        # Prepare the new review data for response
        new_review = {
            'id': new_review_id,
            'game_id': game_id_int,
            'game_name': game_name,
            'user_id': user_id,
            'review': review,
            'time_spent': time_spent_int,
            'rating': rating,
            'date': parsed_date.isoformat()  # Convert to ISO format for consistency
        }
        print('Successfully submitted review')
        return jsonify(new_review), 201  # Return the new review data

    except Exception as e:
        print('Error inserting review:', e)
        return jsonify({'error': 'Internal server error'}), 500

    finally:
        if cursor:
            cursor.close()  # Close the cursor
        if conn:
            release_connection(conn)  # Release the connection back to the pool


# POST route to add in-depth review information
@review_bp.route('/review/in-depth', methods=['POST'])
def add_in_depth_review():
    data = request.json
    print('Received data:', data)  # Log received data

    review_id = data.get('review_id')
    high = data.get('high')
    low = data.get('low')
    atmosphere = data.get('atmosphere')
    story = data.get('story')
    dev_note = data.get('dev_note')
    gameplay = data.get('gameplay')
    difficulty = data.get('difficulty')

    # Validate required fields and their types
    if not all([
        isinstance(review_id, int),
        isinstance(high, str),
        isinstance(low, str),
        isinstance(atmosphere, int),
        isinstance(story, int),
        isinstance(dev_note, str),
        isinstance(gameplay, int),
        isinstance(difficulty, int)
    ]):
        print('Invalid input data:', data)
        return jsonify({'error': 'Invalid input data'}), 400

    connection = None
    try:
        connection = get_connection()  # Get a connection from the pool
        cursor = connection.cursor()

        # Insert in-depth review info into the database
        cursor.execute("""
            INSERT INTO "review_info" (review_id, high, low, atmosphere, story, dev_note, gameplay, difficulty)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING *;
        """, (review_id, high, low, atmosphere, story, dev_note, gameplay, difficulty))

        connection.commit()
        new_review_info = cursor.fetchone()  # Get the newly inserted review info
        print('Successfully submitted in-depth review!', new_review_info)
        return jsonify(new_review_info), 201  # Return the new review info

    except Exception as e:
        print('Error inserting review info:', str(e))  # Log the exception message
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        if connection:
            release_connection(connection)  # Ensure the connection is released


# GET route to fetch in-depth review information by review ID
@review_bp.route('/review/in-depth/<int:review_id>', methods=['GET'])
def get_in_depth_review(review_id):
    print('review Id: ',review_id )
    connection = None  # Initialize the connection variable
    try:
        connection = get_connection()  # Get a connection from the pool
        cursor = connection.cursor()

        # Fetch the review information based on review_id
        cursor.execute(
            'SELECT * FROM "review_info" WHERE review_id = %s',
            (review_id,)
        )
        review_info = cursor.fetchone()  # Get the first result

        if not review_info:
            return jsonify({'error': 'Review not found'}), 404

        # Assuming you have a method to serialize the review info
        print('Retrieving data: ', review_info)
        return jsonify(review_info), 200  # Return the review info

    except Exception as e:
        print('Error fetching review info:', e)
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        if connection:
            release_connection(connection)  # Release the connection back to the pool


# GET route to fetch reviews by username
@review_bp.route('/reviews/user/<string:username>', methods=['GET'])
def get_reviews_by_user(username):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = sql.SQL("""
            SELECT r.id, r.game_name, r.review, r.time_spent, r.rating, r.date, g.cover
            FROM reviews r
            JOIN "Users" u ON r.user_id = u.id
            JOIN games g ON r.game_name = g.name
            WHERE u.username = %s
        """)
        
        cursor.execute(query, (username,))
        rows = cursor.fetchall()
        
        # Convert rows to a more usable format
        reviews = []
        for row in rows:
            reviews.append({
                'id': row[0],          # Review ID
                'game_name': row[1],   # Game Name
                'review': row[2],      # Review text
                'time_spent': row[3],  # Time spent on the game
                'rating': row[4],      # Rating
                'date': row[5],
                'cover': row[6]        # Game cover image
            })

        return jsonify(reviews), 200
    
    except Exception as error:
        print('Error fetching reviews by user:', error)
        return jsonify({'error': 'Internal server error'}), 500
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# GET route to fetch reviews by game name
@review_bp.route('/reviews/game/<string:game>', methods=['GET'])
def get_reviews_by_game(game):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = sql.SQL("""
            SELECT r.id, r.game_name, r.review, r.rating, r.date, r.time_spent, u.username, g.cover
            FROM reviews r
            JOIN games g ON r.game_name = g.name
            JOIN "Users" u on r.user_id = u.id
            WHERE r.game_name = %s
        """)
        
        cursor.execute(query, (game,))
        rows = cursor.fetchall()
        
        # Optionally, convert rows to a more usable format
        reviews = []
        for row in rows:
            reviews.append({
                'id': row[0],  # Adjust index based on your database schema
                'game_name': row[1],  # Adjust as per your schema
                'review': row[2],  # Adjust as per your schema
                'rating': row[3],  # Adjust as per your schema
                'date': row[4],  # Adjust as per your schema
                'time_spent': row[5],
                'username': row[6],
                'cover': row[-1]  # Assuming cover is the last column
            })

        return jsonify(reviews), 200
    
    except Exception as error:
        print('Error fetching reviews by game:', error)
        return jsonify({'error': 'Internal server error'}), 500
    
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# GET route to fetch recent reviews
@review_bp.route('/recentReviews', methods=['GET'])
def get_recent_reviews():
    connection = None
    try:
        # Get a connection from the pool
        connection = get_connection()
        cursor = connection.cursor()
        
        query = """
            SELECT 
            reviews.id,
            reviews.rating,
            reviews.review,
            reviews.date,
            reviews.time_spent,
            games.cover,
            "Users".username
            FROM reviews
            JOIN games ON reviews.game_name = games.name
            JOIN "Users" ON reviews.user_id = "Users".id
            ORDER BY reviews.date DESC
            LIMIT 10;
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()

        reviews = []
        for row in rows:
            reviews.append({
                'id': row[0],
                'rating': row[1],
                'review': row[2],
                'date': row[3],
                'time_spent': row[4],
                'cover': row[5],
                'username': row[6]
            })

        cursor.close()
        return jsonify(reviews), 200
    except Exception as error:
        print(f"Error fetching recent reviews: {error}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        # Release the connection back to the pool
        if connection:
            release_connection(connection)