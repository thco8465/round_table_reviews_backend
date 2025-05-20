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
    cover_url = data.get('cover')
    user_id = data.get('userId')
    review = data.get('review')
    time_spent = data.get('timeSpent')
    rating = data.get('rating')
    date = data.get('date')

    # Validate required fields and their types
    if not all([isinstance(game_id, int), isinstance(game_name, str), isinstance(cover_url, str), isinstance(user_id, int), 
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
            INSERT INTO reviews (game_id, game_name, cover_url,user_id, review, time_spent, rating, date)
            VALUES (%s, %s, %s,%s, %s, %s, %s, %s) RETURNING id;
        """)

        # Execute the insert query
        cursor.execute(insert_query, (game_id_int, game_name, cover_url,user_id, review, time_spent_int, rating, parsed_date))
        new_review_id = cursor.fetchone()[0]  # Get the ID of the newly inserted review

        # Commit the transaction
        conn.commit()

        # Prepare the new review data for response
        new_review = {
            'id': new_review_id,
            'game_id': game_id_int,
            'game_name': game_name,
            'cover_url': cover_url,
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
            """
            SELECT r.*, reviews.cover_url, reviews.game_name
            FROM review_info r
            JOIN reviews ON r.review_id = reviews.id
            WHERE r.review_id = %s
            """,
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
            SELECT r.id, r.game_name, r.review, r.time_spent, r.rating, r.date, r.cover_url
            FROM reviews r
            JOIN "Users" u ON r.user_id = u.id
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
        SELECT r.id, r.game_name, r.review, r.rating, r.date, r.time_spent, u.username, r.cover_url
        FROM reviews r
        JOIN "Users" u ON r.user_id = u.id
        WHERE r.game_name ILIKE %s
    """)
        
        cursor.execute(query, (f"%{game}%",))
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
            reviews.cover_url,
            "Users".username,
            reviews.game_name
            FROM reviews
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
                'username': row[6],
                'game_name': row[7]
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
# POST route to add or update a vote on a review
@review_bp.route('/review/vote', methods=['POST'])
def vote_review():
    data = request.json
    review_id = data.get('reviewId')
    user_id = data.get('userId')
    vote = data.get('vote')  # Expected to be 1 (helpful) or -1 (not helpful)

    # Validate input
    if vote not in [1, -1]:
        print("Invalid vote value:", vote)
        return jsonify({'error': 'Vote must be 1 (helpful) or -1 (not helpful)'}), 400

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Use INSERT ... ON CONFLICT to insert or update the vote
        vote_query = """
            INSERT INTO review_votes (review_id, user_id, vote)
            VALUES (%s, %s, %s)
            ON CONFLICT (review_id, user_id)
            DO UPDATE SET vote = EXCLUDED.vote, created_at = now();
        """
        cursor.execute(vote_query, (review_id, user_id, vote))
        conn.commit()

        # After recording the vote, update the reviews table with aggregated counts.
        update_query = """
            UPDATE reviews
            SET helpful_votes = (
                  SELECT COUNT(*) FROM review_votes 
                  WHERE review_id = %s AND vote = 1
                ),
                not_helpful_votes = (
                  SELECT COUNT(*) FROM review_votes 
                  WHERE review_id = %s AND vote = -1
                )
            WHERE id = %s;
        """
        cursor.execute(update_query, (review_id, review_id, review_id))
        conn.commit()

        return jsonify({'message': 'Vote recorded successfully'}), 201

    except Exception as e:
        print('Error recording vote:', e)
        if conn:
            conn.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)



# POST route to add a comment to a review
@review_bp.route('/review/comment', methods=['POST'])
def post_comment():
    data = request.json
    review_id = data.get('reviewId')
    user_id = data.get('userId')
    comment_text = data.get('comment')

    # Validate required fields
    if not all([review_id, user_id, comment_text]) or not isinstance(comment_text, str):
        print("Invalid comment data:", data)
        return jsonify({'error': 'Invalid input data'}), 400

    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        comment_query = """
            INSERT INTO review_comments (review_id, user_id, comment)
            VALUES (%s, %s, %s) RETURNING id, created_at;
        """
        cursor.execute(comment_query, (review_id, user_id, comment_text))
        new_comment = cursor.fetchone()
        conn.commit()

        response = {
            'id': new_comment[0],
            'reviewId': review_id,
            'userId': user_id,
            'comment': comment_text,
            'createdAt': new_comment[1].isoformat()
        }
        return jsonify(response), 201

    except Exception as e:
        print('Error inserting comment:', e)
        conn.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)


# GET route to fetch all comments for a specific review
@review_bp.route('/review/<int:review_id>/comments', methods=['GET'])
def get_comments(review_id):
    conn = None
    cursor = None
    try:
        conn = get_connection() 
        cursor = conn.cursor()
        
        query = """
            SELECT rc.id, rc.comment, rc.created_at, u.username
            FROM review_comments rc
            LEFT JOIN "Users" u ON rc.user_id = u.id
            WHERE rc.review_id = %s
            ORDER BY rc.created_at DESC;
        """
        cursor.execute(query, (review_id,))
        rows = cursor.fetchall()
        
        comments = []
        for row in rows:
            comments.append({
                'id': row[0],
                'comment': row[1],
                'createdAt': row[2].isoformat(),
                'username': row[3]  # Assuming the Users table has a username column
            })

        return jsonify(comments), 200

    except Exception as e:
        print('Error fetching comments:', e)
        return jsonify({'error': 'Internal server error'}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)
@review_bp.route('/review/vote/<int:review_id>', methods=['GET'])
def get_review_votes(review_id):
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Select the aggregated vote counts directly from the reviews table
        query = """
            SELECT helpful_votes, not_helpful_votes
            FROM reviews
            WHERE id = %s;
        """
        cursor.execute(query, (review_id,))
        row = cursor.fetchone()
        
        if not row:
            return jsonify({'error': 'Review not found'}), 404

        helpful, not_helpful = row
        
        return jsonify({
            'reviewId': review_id,
            'helpfulVotes': helpful,
            'notHelpfulVotes': not_helpful
        }), 200

    except Exception as e:
        print('Error fetching votes:', e)
        return jsonify({'error': 'Internal server error'}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            release_connection(conn)
