import os
from flask import Flask, jsonify
from flask_cors import CORS
from routes.authRoutes import auth_bp
from routes.games import game_bp
from routes.review import review_bp
from routes.twitch_api import twitch_bp
from routes.user import user_bp
from models import db, Game, Users, Review, ReviewInfo  # Import the db object
from flask_migrate import Migrate, upgrade

app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "*"}})  # Allow all origins for API routes

# Use the DATABASE_URL environment variable
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the db object with the app
db.init_app(app)  

# Initialize Flask-Migrate
migrate = Migrate(app, db)  

def apply_migrations():
    with app.app_context():
        try:
            # Run this to apply any pending migrations
            upgrade()  
            print("Migrations applied successfully.")
        except Exception as e:
            print(f"Error applying migrations: {e}")

# Apply migrations at startup
apply_migrations()

# Register your blueprints
app.register_blueprint(auth_bp, url_prefix='/api/authRoutes')
app.register_blueprint(game_bp, url_prefix='/api/games')
app.register_blueprint(review_bp, url_prefix='/api/review')
app.register_blueprint(twitch_bp, url_prefix='/api/twitch_api')
app.register_blueprint(user_bp, url_prefix='/api/user')

@app.route('/')
def home():
    return "Hello, Flask!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
