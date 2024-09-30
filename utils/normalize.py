# /utils/normalize.py

import re

def normalize_game_name(name):
    if not name:
        return ''

    # Trim whitespace
    normalized = name.strip()

    # Convert to title case
    normalized = normalized.title()

    # Remove special characters (except hyphens and apostrophes)
    normalized = re.sub(r"[^\w\s'-]", '', normalized)

    # Replace multiple spaces with a single space
    normalized = re.sub(r'\s+', ' ', normalized)

    return normalized
