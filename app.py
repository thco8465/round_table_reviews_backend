# from flask import Flask
# from routes.user_routes import user_routes
# from routes.product_routes import product_routes
# from routes.order_routes import order_routes

# app = Flask(__name__)

# app.register_blueprint(user_routes, url_prefix='/api')
# app.register_blueprint(product_routes, url_prefix='/api')
# app.register_blueprint(order_routes, url_prefix='/api')

import os
from flask import Flask, jsonify
from flask_cors import CORS
from routes.authRoutes import auth_bp
from routes.games import game_bp
from routes.review import review_bp
from routes.twitch_api import twitch_bp
from routes.user import user_bp
from models import db, Game, Users, Review, ReviewInfo  # Import the db object
from flask_migrate import Migrate

app = Flask(__name__)

CORS(app, resources={r"/api/*": {"origins": "*"}})  # Allow all origins for API routes


#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:ArkhamknightN7?@localhost:5432/gamespective'  # Update with your database URI
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')  # Update with your database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)  # Initialize the db object with the app
migrate = Migrate(app, db)  # Initialize Flask-Migrate

with app.app_context():
    db.create_all()  # Create the tables

app.register_blueprint(auth_bp, url_prefix='/api/authRoutes')
app.register_blueprint(game_bp, url_prefix='/api/games')
app.register_blueprint(review_bp, url_prefix='/api/review')
app.register_blueprint(twitch_bp, url_prefix='/api/twitch_api')
app.register_blueprint(user_bp, url_prefix='/api/user')




@app.route('/')
def home():
    return "Hello, Flask!"
# @app.route('/api/data', methods=['GET'])
# def get_date():
#     return jsonify({"message": "Hello from Flask!"})
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
