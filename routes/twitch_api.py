from flask import Blueprint, request, jsonify
import requests
import os
from utils.twitch_api_utils import get_valid_token  # Import your utility function

twitch_bp = Blueprint('twitch', __name__)

client_id = os.getenv('TWITCH_CLIENT_ID')  # Ensure to import os if you haven't

@twitch_bp.route('/games', methods=['GET'])
def get_game_data():
    print('Inside /games - Fetching game data...')
    game_name = request.args.get('name')

    if not game_name:
        return jsonify({'error': 'Game name is required'}), 400

    try:
        access_token = get_valid_token()  # Ensure we have a valid token
        print('Access Token:', access_token)  # Log the access token

        if not access_token:
            return jsonify({'error': 'Could not get access token'}), 500

        headers = {
            'Client-ID': client_id,
            'Authorization': f'Bearer {access_token}',
            'ngrok-skip-browser-warning': '69420'  # Add this header to skip ngrok warning
        }

        api_url = f'https://api.twitch.tv/helix/games?name={game_name}'
        print('Requesting URL:', api_url)  # Log the URL being requested

        response = requests.get(api_url, headers=headers)

        # Log the response status and text for debugging
        print('Twitch API Status Code:', response.status_code)
        print('Twitch API Raw Response:', response.text)  # Log the raw response

        # Check for a successful response
        if response.status_code != 200:
            return jsonify({'error': 'Error fetching game data from Twitch API', 'details': response.text}), response.status_code

        # Attempt to parse JSON response
        try:
            data = response.json()
        except ValueError as e:
            return jsonify({'error': 'Error parsing response JSON', 'details': str(e), 'raw_response': response.text}), 500

        if data.get('data'):
            game = data['data'][0]
            game_id = game['id']
            game_title = game['name']
            cover_image = game['box_art_url'].replace('{width}', '300').replace('{height}', '400')
            return jsonify({'gameId': game_id, 'title': game_title, 'cover': cover_image}), 200
        else:
            return jsonify({'error': 'Game not found'}), 404
            
    except Exception as e:
        print('Error fetching game data:', e)
        return jsonify({'error': 'Error fetching game data', 'details': str(e)}), 500