from flask import Blueprint, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from utils.databaseOperations import insert_or_update_game
from utils.dataProcessing import fetch_and_normalize_game_names
from utils.populateGames import populate_games_table
from utils.normalize import normalize_game_name
from utils.twitch_api_utils import get_valid_token

game_bp = Blueprint('games', __name__)
db = SQLAlchemy()  # Initialize your database

# GET route to retrieve all games from the database
@game_bp.route('/games', methods=['GET'])
def get_games():
    try:
        games = db.session.execute('SELECT id, name, normalized_name, cover, description FROM games').fetchall()
        if games:
            print('Games data retrieved:', games)
            return jsonify([dict(row) for row in games])  # Convert rows to dict
        else:
            return jsonify({'error': 'No games found'}), 404
    except Exception as e:
        print('Error fetching games data:', e)
        return jsonify({'error': 'Internal Server Error'}), 500

# GET route to search games
@game_bp.route('/search-games', methods=['GET'])
def search_games():
    try:
        search_term = request.args.get('name')  # Get the search term from query parameters
        if not search_term:
            return jsonify({'error': 'Search term is required'}), 400

        query = '''
            SELECT id, name, cover
            FROM games
            WHERE name ILIKE :search_term
            LIMIT 10;
        '''  # Using ILIKE for case-insensitive search

        result = db.session.execute(query, {'search_term': f'%{search_term}%'})
        rows = result.fetchall()

        if rows:
            print('Search results:', rows)
            return jsonify([dict(row) for row in rows])
        else:
            return jsonify({'error': 'No games found'}), 404
    except Exception as e:
        print('Error searching games:', e)
        return jsonify({'error': 'Internal Server Error'}), 500

# POST route to add or update a game in the database
@game_bp.route('/games', methods=['POST'])
def add_or_update_game():
    try:
        game = request.get_json()  # Ensure to validate and sanitize input
        game['name'] = normalize_game_name(game['name'])  # Normalize game name
        insert_or_update_game(game)
        return jsonify({'message': 'Game added or updated successfully'}), 201
    except Exception as e:
        print('Error processing game:', e)
        return jsonify({'error': 'Internal Server Error'}), 500

# GET route to fetch and normalize game names from Twitch API
@game_bp.route('/fetch-games', methods=['GET'])
def fetch_games():
    try:
        access_token = get_valid_token()  # Ensure we have a valid token

        if not access_token:
            return jsonify({'error': 'Could not get access token'}), 500

        games = fetch_and_normalize_game_names(access_token)  # Fetch and normalize game names
        return jsonify(games)
    except Exception as e:
        print('Error fetching and processing game names:', e)
        return jsonify({'error': 'Internal Server Error'}), 500

# POST route to populate the games table
@game_bp.route('/populate-games', methods=['POST'])
def populate_games():
    try:
        populate_games_table()  # Call the function to populate the games table
        return jsonify({'message': 'Games table populated successfully'}), 201
    except Exception as e:
        print('Error populating games table:', e)
        return jsonify({'error': 'Internal Server Error'}), 500
