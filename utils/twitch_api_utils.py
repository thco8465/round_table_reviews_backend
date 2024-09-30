import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

client_id = os.getenv('TWITCH_CLIENT_ID')
client_secret = os.getenv('TWITCH_CLIENT_SECRET')
token_file_path = '../twitch_token.json'  # Path to store token and expiry

def get_access_token():
    try:
        print('Fetching new access token...')
        response = requests.post('https://id.twitch.tv/oauth2/token', data={
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'client_credentials'
        })

        data = response.json()
        print('Access token response:', data)

        # Store the token and expiry time in a file
        token_data = {
            'access_token': data['access_token'],
            'expires_at': (datetime.now() + timedelta(seconds=data['expires_in'])).isoformat()  # Store expiry time as ISO 8601
        }
        with open(token_file_path, 'w') as token_file:
            json.dump(token_data, token_file, indent=2)

        print('Access token saved to file.')
        return token_data['access_token']
    except Exception as error:
        print('Error fetching access token:', error)
        return None

def get_valid_token():
    print('Checking for valid token...')
    if os.path.exists(token_file_path):
        with open(token_file_path, 'r') as token_file:
            token_data = json.load(token_file)
        print('Token data from file:', token_data)

        # Convert expires_at to a datetime object for comparison
        expires_at = datetime.fromisoformat(token_data['expires_at'])
        if datetime.now() < expires_at:
            print('Token is still valid.')
            return token_data['access_token']  # Token is still valid

    # Token has expired or doesn't exist, fetch a new one
    print('Token is expired or does not exist, fetching new token...')
    return get_access_token()
