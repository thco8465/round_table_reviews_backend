from app import app  # or wherever you create your Flask app and initialize db
from models import db

with app.app_context():
    db.create_all()
    print("All tables created successfully!")
