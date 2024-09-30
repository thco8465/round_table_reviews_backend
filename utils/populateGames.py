import os
import asyncio
import logging
from dotenv import load_dotenv
from .dataProcessing import fetch_and_normalize_game_names
from .databaseOperations import insert_or_update_game

load_dotenv()

async def populate_games_table():
    logging.debug('populate_games_table called')
    cursor = None
    total_games = 0

    while True:
        # Fetch and normalize a batch of games
        games_data = await fetch_and_normalize_game_names(cursor)
        games = games_data['games']
        new_cursor = games_data.get('cursor')

        # Insert the games into the database
        await insert_or_update_game(games)

        total_games += len(games)
        cursor = new_cursor  # Update the cursor for the next batch

        logging.info(f'Inserted {total_games} games so far...')

        if not cursor or total_games >= 1:  # Change this condition based on your needs
            break

    logging.info('Successfully populated the games table with all Twitch games!')

if __name__ == '__main__':
    if os.getenv('POPULATE_GAMES') == 'true':
        asyncio.run(populate_games_table())
