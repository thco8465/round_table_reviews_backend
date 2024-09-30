from flask import Blueprint, request, jsonify
from functools import wraps
import jwt
import os
from db import get_connection, release_connection  # Import connection functions
user_bp = Blueprint('user', __name__)

# Middleware to check if the user is authenticated
def authenticate(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token:
            token = token.split(' ')[1]  # Extract token from "Bearer <token>"
        else:
            return jsonify({'error': 'Unauthorized'}), 401

        try:
            decoded = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=["HS256"])
            request.user = {'id': decoded['id']}  # Set user ID to request object
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Unauthorized'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Unauthorized'}), 401
    return decorated

# Get user information
@user_bp.route('/me', methods=['GET'])
@authenticate
def get_user_info():
    try:
        user_id = request.user['id']  # Get user ID from request
        
        # Get a connection from the pool
        conn = get_connection()

        try:
            # Create a cursor to execute the query
            with conn.cursor() as cursor:
                query = '''
                    SELECT id, "firstName", "username", "reviewCount", exp, level
                    FROM "Users"
                    WHERE id = %s
                '''
                cursor.execute(query, (user_id,))

                # Fetch the user data
                user = cursor.fetchone()

                if user:
                    # Return user info as JSON
                    return jsonify({
                        'id': user[0],
                        'firstName': user[1],
                        'username': user[2],
                        'reviewCount': user[3],
                        'exp': user[4],
                        'level': user[5]
                    })
                else:
                    return jsonify({'error': 'User not found'}), 404
        finally:
            # Always release the connection back to the pool
            release_connection(conn)
    except Exception as error:
        print('Error fetching user data:', error)
        return jsonify({'error': 'Internal Server Error'}), 500
    
@user_bp.route('/reviewCount', methods=['POST'])
@authenticate
def update_review_count():
    try:
        user_id = request.user['id']  # Get authenticated user ID
        print('Authenticated user ID', user_id)

        # Get a connection from the pool
        conn = get_connection()

        try:
            # Create a cursor to execute the update and select queries
            with conn.cursor() as cursor:
                # Update review count
                update_query = '''
                    UPDATE "Users" 
                    SET "reviewCount" = "reviewCount" + 1 
                    WHERE id = %s
                '''
                cursor.execute(update_query, (user_id,))
                
                # Fetch the updated review count
                select_query = '''
                    SELECT "reviewCount" 
                    FROM "Users" 
                    WHERE id = %s
                '''
                cursor.execute(select_query, (user_id,))
                
                # Fetch the result
                update_count = cursor.fetchone()[0]
                print('Updated review count:', update_count)

                # Commit the transaction to persist changes
                conn.commit()

                # Return the updated review count as JSON
                return jsonify({'reviewCount': update_count})
        finally:
            # Always release the connection back to the pool
            release_connection(conn)
    except Exception as error:
        print('Error updating review count:', error)
        return jsonify({'error': 'Internal Server Error'}), 500
    
@user_bp.route('/exp', methods=['POST'])
@authenticate
def update_experience():
    try:
        user_id = request.user['id']  # Get authenticated user ID
        exp = request.json.get('exp')  # Amount of experience being added

        # Validate the input
        if not isinstance(exp, (int, float)) or exp < 0:
            return jsonify({'error': 'Invalid experience value'}), 400

        # Get a connection from the pool
        conn = get_connection()

        try:
            # Fetch current user data (exp and level)
            with conn.cursor() as cursor:
                user_query = '''
                    SELECT exp, level 
                    FROM "Users" 
                    WHERE id = %s
                '''
                cursor.execute(user_query, (user_id,))
                user = cursor.fetchone()

                if not user:
                    return jsonify({'error': 'User not found'}), 404

                current_exp = user[0]
                current_level = user[1]

                # Calculate new experience and level
                total_exp = current_exp + exp  # New total experience
                levels = [
                    'Serf', 'Peasant', 'Apprentice', 'Squire', 'Journeyman',
                    'Yeoman', 'Footman', 'Knight', 'Master', 'Captain', 'Baron',
                    'Viscount', 'Earl', 'Duke', 'Grandmaster', 'Champion', 'Lord',
                    'Lady', 'King', 'Queen', 'Emperor', 'Empress', 'Sovereign'
                ]  # List of levels based on experience

                # Calculate new level based on total experience
                level_index = total_exp // 100  # Every 100 exp corresponds to the next level
                new_level = levels[min(level_index, len(levels) - 1)]  # Prevent going beyond max level

                # Update the user's experience and level in the database
                update_query = '''
                    UPDATE "Users" 
                    SET exp = %s, level = %s 
                    WHERE id = %s 
                    RETURNING exp, level
                '''
                cursor.execute(update_query, (total_exp, new_level, user_id))

                # Fetch the updated experience and level
                updated_user = cursor.fetchone()

                # Commit the transaction to persist changes
                conn.commit()

                # Return the updated experience and level
                return jsonify({
                    'exp': updated_user[0],
                    'level': updated_user[1]
                })
        finally:
            # Always release the connection back to the pool
            release_connection(conn)
    except Exception as error:
        print('Error updating experience and level:', error)
        return jsonify({'error': 'Internal Server Error'}), 500
    
# Get all reviews for authenticated user
@user_bp.route('/displayReviews', methods=['GET'])
@authenticate
def display_reviews():
    try:
        user_id = request.user['id']  # Get the authenticated user ID

        # Get a connection from the pool
        conn = get_connection()

        try:
            # Fetch reviews for the authenticated user
            with conn.cursor() as cursor:
                reviews_query = """
                    SELECT reviews.id, reviews.rating, reviews.review, reviews.date, reviews.game_name, games.cover
                    FROM reviews
                    JOIN games ON similarity(reviews.game_name, games.name) > 0.8
                    WHERE reviews.user_id = %s
                    ORDER BY reviews.date DESC
                """
                cursor.execute(reviews_query, (user_id,))
                reviews = cursor.fetchall()  # Get all the reviews

                if reviews:
                    # Convert reviews to a list of dictionaries for JSON response
                    review_list = [
                        {
                            'id': row[0],
                            'rating': row[1],
                            'review': row[2],
                            'date': row[3],
                            'game_name': row[4],
                            'cover': row[5]
                        }
                        for row in reviews
                    ]
                    return jsonify(review_list)
                else:
                    return jsonify({'error': 'No reviews found for this user'}), 404
        finally:
            # Release the connection back to the pool
            release_connection(conn)
    except Exception as error:
        print('Error fetching reviews:', error)
        return jsonify({'error': 'Internal Server Error'}), 500
    
# Get all accepted friends for a user
@user_bp.route('/friends', methods=['GET'])
async def get_friends():
    user_id = request.args.get('id', type=int)  # Convert to number
    print('user id:', user_id)

    if user_id is None:
        return jsonify({'message': 'Invalid userId'}), 400

    conn = None
    cursor = None
    try:
        conn = get_connection()  # Obtain connection from the pool
        cursor = conn.cursor()

        query = """
            SELECT f.friend_id, u.username as friend_username, f.status
            FROM friends f
            JOIN "Users" u ON u.id = f.friend_id
            WHERE f.user_id = %s AND f.status = 'accepted';
        """
        
        cursor.execute(query, (user_id,))
        friends = cursor.fetchall()  # Fetch all results
        
        # Format the result
        result = [
            {
                'friend_id': friend[0],
                'friend_username': friend[1],
                'status': friend[2]
            }
            for friend in friends
        ]
        
        return jsonify(result), 200
        
    except Exception as error:
        print('Error fetching friends:', error)
        return jsonify({'message': 'Server error while fetching friends.'}), 500
    
    finally:
        if cursor:
            cursor.close()  # Close the cursor
        if conn:
            release_connection(conn)  # Release the connection back to the pool

# Get user by ID
@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):

    conn = None
    cursor = None
    try:
        conn = get_connection()  # Obtain connection from the pool
        cursor = conn.cursor()

        # SQL query to get user data by ID
        query = 'SELECT * FROM "Users" WHERE id = %s'
        cursor.execute(query, (user_id,))

        if cursor.rowcount == 0:
            return jsonify({'error': 'User not found'}), 404

        user_data = cursor.fetchone()  # Fetch the user data
        
        # Convert the user data to a dictionary for JSON response
        user_dict = {
            'id': user_data[0],  # Adjust indices based on your schema
            'username': user_data[-1],  # Adjust as needed
            'reviewCount': user_data[-4],  # Adjust as needed
            'exp': user_data[-3],
            'level': user_data[-2],
            # Add other fields as needed
        }

        return jsonify(user_dict), 200

    except Exception as error:
        print('Error fetching user data:', error)
        return jsonify({'error': 'Internal server error'}), 500
    
    finally:
        if cursor:
            cursor.close()  # Close the cursor
        if conn:
            release_connection(conn)  # Release the connection back to the pool

# Get user reviews by user ID
@user_bp.route('/<int:user_id>/reviews', methods=['GET'])
async def get_user_reviews(user_id):
    conn = None
    cursor = None
    try:
        conn = get_connection()  # Obtain connection from the pool
        cursor = conn.cursor()

        query = """
            SELECT reviews.id, reviews.rating, reviews.review, reviews.date, reviews.game_name, games.cover
            FROM reviews
            JOIN games ON similarity(reviews.game_name, games.name) > 0.8
            WHERE reviews.user_id = %s
            ORDER BY reviews.date DESC
        """

        cursor.execute(query, (user_id,))
        reviews = cursor.fetchall()  # Fetch all results

        # Convert rows to a more usable format
        result = [
            {
                'id': review[0],
                'rating': review[1],
                'review': review[2],
                'date': review[3],
                'game_name': review[4],
                'cover': review[5]
            }
            for review in reviews
        ]

        return jsonify(result), 200

    except Exception as error:
        print('Error fetching user reviews:', error)
        return jsonify({'error': 'Internal server error'}), 500
    
    finally:
        if cursor:
            cursor.close()  # Close the cursor
        if conn:
            release_connection(conn)  # Release the connection back to the pool

# Search for users by username
@user_bp.route('/search-user', methods=['GET'])
async def search_user():
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'Username parameter is required'}), 400  # Validate input

    conn = None
    cursor = None
    try:
        conn = get_connection()  # Obtain connection from the pool
        cursor = conn.cursor()

        # Parameterized query to prevent SQL injection
        query = 'SELECT id, username FROM "Users" WHERE username ILIKE %s'
        cursor.execute(query, (f'%{username}%',))

        users = cursor.fetchall()  # Fetch all matching users

        # Format the result for response
        result = [{'id': user[0], 'username': user[1]} for user in users]

        return jsonify(result), 200

    except Exception as error:
        print('Error searching for user:', error)
        return jsonify({'error': 'Error searching for user'}), 500

    finally:
        if cursor:
            cursor.close()  # Close the cursor
        if conn:
            release_connection(conn)  # Release the connection back to the pool

# Add a new friend (send friend request)
@user_bp.route('/add-friend', methods=['POST'])
async def add_friend():
    data = request.json
    user_id = data.get('userId')
    friend_id = data.get('friendId')

    if user_id is None or friend_id is None:
        return jsonify({'error': 'Both userId and friendId are required'}), 400

    conn = None
    cursor = None
    try:
        conn = get_connection()  # Get connection from pool
        cursor = conn.cursor()  # Create a cursor object

        # Prepare and execute the query to insert a friend request
        cursor.execute('INSERT INTO friends (user_id, friend_id, status) VALUES (%s, %s, %s)', 
                             [user_id, friend_id, 'pending'])
        
        conn.commit()  # Commit the transaction

        return jsonify({'message': 'Friend request sent'}), 201

    except Exception as error:
        print('Error sending friend request:', error)
        return jsonify({'error': 'Error sending friend request'}), 500

    finally:
        if cursor:
            cursor.close()  # Close the cursor
        if conn:
            release_connection(conn)  # Release connection back to the pool

# Check friendship status
@user_bp.route('/friend-status', methods=['GET'])
async def friend_status():
    user_id = request.args.get('userId', type=int)  # Convert to integer
    friend_id = request.args.get('friendId', type=int)  # Convert to integer

    if user_id is None or friend_id is None:
        return jsonify({'error': 'Both userId and friendId are required'}), 400

    conn = None
    cursor = None
    try:
        conn = get_connection()  # Obtain a connection from the pool
        cursor = conn.cursor()

        query = 'SELECT status FROM friends WHERE user_id = %s AND friend_id = %s'
        cursor.execute(query, (user_id, friend_id))  # Execute the query with parameters
        result = cursor.fetchone()  # Fetch the single result

        if result is None:
            return jsonify({'status': 'not_friends'}), 200  # If no record found, return not_friends

        return jsonify({'status': result[0]}), 200  # Return the friendship status

    except Exception as error:
        print('Error checking friendship status:', error)
        return jsonify({'error': 'Error checking friendship status'}), 500

    finally:
        if cursor:
            cursor.close()  # Close the cursor
        if conn:
            release_connection(conn)  # Release the connection back to the pool


# Get sent friend requests
@user_bp.route('/friends/sent', methods=['GET'])
async def sent_friend_requests():
    user_id = request.args.get('id', type=int)  # Convert to integer

    if user_id is None:
        return jsonify({'error': 'User ID is required'}), 400

    conn = None
    cursor = None
    try:
        conn = get_connection()  # Obtain a connection from the pool
        cursor = conn.cursor()

        query = """
            SELECT 
                u2.username AS friend_username,
                f.status,
                f.friend_id AS friend_id
            FROM 
                friends f
            JOIN 
                "Users" u2 ON f.friend_id = u2.id
            WHERE 
                f.user_id = %s
        """
        cursor.execute(query, (user_id,))  # Execute the query with parameters
        result = cursor.fetchall()  # Fetch all results

        # Convert result to a list of dictionaries
        sent_requests = [{'friend_username': row[0], 'status': row[1], 'friend_id': row[2]} for row in result]

        return jsonify(sent_requests), 200  # Return the list of sent friend requests

    except Exception as error:
        print('Error fetching sent friend requests:', error)
        return jsonify({'error': 'Internal Server Error'}), 500

    finally:
        if cursor:
            cursor.close()  # Close the cursor
        if conn:
            release_connection(conn)  # Release the connection back to the pool

# Get received friend requests
@user_bp.route('/friends/received', methods=['GET'])
async def received_friend_requests():
    user_id = request.args.get('id', type=int)  # Convert to integer

    if user_id is None:
        return jsonify({'error': 'User ID is required'}), 400

    conn = None
    cursor = None
    try:
        conn = get_connection()  # Obtain a connection from the pool
        cursor = conn.cursor()

        query = """
            SELECT 
                u.username AS friend_username,
                f.status,
                f.user_id AS friend_id
            FROM 
                friends f
            JOIN 
                "Users" u ON f.user_id = u.id
            WHERE 
                f.friend_id = %s
        """
        cursor.execute(query, (user_id,))  # Execute the query with parameters
        result = cursor.fetchall()  # Fetch all results

        # Convert result to a list of dictionaries
        requests = [{'friend_username': row[0], 'status': row[1], 'friend_id': row[2]} for row in result]

        return jsonify(requests), 200  # Return the list of received friend requests

    except Exception as error:
        print('Error fetching received friend requests:', error)
        return jsonify({'error': 'Internal Server Error'}), 500

    finally:
        if cursor:
            cursor.close()  # Close the cursor
        if conn:
            release_connection(conn)  # Release the connection back to the pool

# Accept a friend request
@user_bp.route('/friends/accept', methods=['POST'])
async def accept_friend_request():
    data = request.json
    user_id = data.get('userId')
    friend_id = data.get('friendId')

    if user_id is None or friend_id is None:
        return jsonify({'message': 'userId and friendId are required'}), 400  # Validate input

    conn = None
    cursor = None
    try:
        conn = get_connection()  # Obtain connection from the pool
        cursor = conn.cursor()

        query = """
            UPDATE friends
            SET status = 'accepted'
            WHERE user_id = %s AND friend_id = %s AND status = 'pending'
            RETURNING *;
        """
        values = [user_id, friend_id]  # Ensure correct order for parameters

        cursor.execute(query, values)  # Execute the query
        result = cursor.fetchone()  # Fetch the result

        if not result:
            return jsonify({'message': 'Friend request not found or already processed.'}), 404

        conn.commit()
        return jsonify({'message': 'Friend request accepted.', 'data': result})

    except Exception as error:
        print('Error accepting friend request:', error)
        return jsonify({'message': 'Server error while accepting friend request.'}), 500

    finally:
        if cursor:
            cursor.close()  # Close the cursor
        if conn:
            release_connection(conn)  # Release the connection back to the pool

#Decline a friend request
@user_bp.route('/friends/decline', methods=['POST'])
async def decline_friend_request():
    data = request.json
    user_id = data.get('userId')
    friend_id = data.get('friendId')

    if user_id is None or friend_id is None:
        return jsonify({'message': 'userId and friendId are required'}), 400  # Validate input

    conn = None
    cursor = None
    try:
        conn = get_connection()  # Obtain connection from the pool
        cursor = conn.cursor()

        query = """
            UPDATE friends
            SET status = 'declined'
            WHERE user_id = %s AND friend_id = %s AND status = 'pending'
            RETURNING *;
        """
        values = [user_id, friend_id]  # Ensure correct order for parameters

        cursor.execute(query, values)  # Execute the query
        result = cursor.fetchone()  # Fetch the result

        if not result:
            return jsonify({'message': 'Friend request not found or already processed.'}), 404

        conn.commit()
        return jsonify({'message': 'Friend request declined.', 'data': result})

    except Exception as error:
        print('Error declining friend request:', error)
        return jsonify({'message': 'Server error while declining friend request.'}), 500

    finally:
        if cursor:
            cursor.close()  # Close the cursor
        if conn:
            release_connection(conn)  # Release the connection back to the pool
# Note: Ensure you have configured your asyncpg connection pooling correctly in the utils/db.py module.

#unfriend someone from from friends table using friend_id
@user_bp.route('/friends/unfriend/<int:friend_id>', methods=['DELETE'])
def unfriend_user(friend_id):
    conn = None
    cursor = None
    try:
        conn = get_connection()  # Get connection from the pool
        cursor = conn.cursor()

        # Check if the friend exists in the friends table
        query = 'SELECT * FROM friends WHERE friend_id = %s'
        cursor.execute(query, (friend_id,))

        # If no matching friend is found, return a 404 error
        if cursor.rowcount == 0:
            return jsonify({'error': 'Friend not found'}), 404

        # If the friend exists, proceed to delete the row from the friends table
        delete_query = 'DELETE FROM friends WHERE friend_id = %s'
        cursor.execute(delete_query, (friend_id,))

        conn.commit()  # Commit the transaction

        return jsonify({'message': 'Successfully unfriended'}), 200

    except Exception as error:
        print('Error during unfriending:', error)
        return jsonify({'error': 'Internal server error'}), 500
    
    finally:
        if cursor:
            cursor.close()  # Close the cursor
        if conn:
            release_connection(conn)  # Release the connection back to the pool
