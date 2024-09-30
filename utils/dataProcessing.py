import os
import requests
from .normalize import normalize_game_name  # Import your normalization function
from .twitch_api_utils import get_valid_token  # Import your token fetching function

client_id = os.getenv('TWITCH_CLIENT_ID')

def fetch_and_normalize_game_names(cursor=None):
    try:
        # Get a valid token
        access_token = get_valid_token()
        if not access_token:
            raise ValueError('No valid access token available')

        # Fetch data from Twitch API
        url = 'https://api.twitch.tv/helix/games/top'
        params = {}
        if cursor:
            params['after'] = cursor

        headers = {
            'Client-ID': client_id,
            'Authorization': f'Bearer {access_token}',
        }

        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        print('Twitch API Response Data:', data)

        if 'data' not in data or not isinstance(data['data'], list):
            raise ValueError('Invalid data format from Twitch API')

        # Example of normalization
        games = [{
            'name': game.get('name', 'Unknown'),  # Default to 'Unknown' if name is missing
            'normalized_name': normalize_game_name(game.get('name', 'Unknown')),  # Ensure normalized_name is set
            'cover': game.get('box_art_url', ''),  # Use box_art_url for cover
            'description': ''  # No description field available
        } for game in data['data']]

        # Return data with cursor for pagination if needed
        return {
            'games': games,
            'cursor': data.get('pagination', {}).get('cursor', None)
        }

    except Exception as error:
        print('Error in fetch_and_normalize_game_names:', error)
        raise  # Rethrow error after logging
