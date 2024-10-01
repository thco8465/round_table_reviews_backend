from flask import Blueprint, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import jwt
import os
import traceback
from models import db,Users  # Ensure your User model is correctly imported

auth_bp = Blueprint('auth', __name__)
#db = SQLAlchemy()  # Initialize your database
bcrypt = Bcrypt()  # Initialize Bcrypt for password hashing

@auth_bp.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        print('Sign-up request received with data:', data)  # Log the received data

        first_name = data.get('firstName')
        last_name = data.get('lastName')
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        # Validate input
        if not all([first_name, last_name, username, email, password]):
            print('Validation failed: Missing required fields')
            return jsonify({'error': 'All fields are required'}), 400

        # Check if the email is already in use
        existing_email_user = Users.query.filter_by(email=email).first()
        if existing_email_user:
            print('Email already in use:', email)
            return jsonify({'error': 'Email is already in use'}), 400

        # Check if the username is already in use
        existing_username_user = Users.query.filter_by(username=username).first()
        if existing_username_user:
            print('Username already in use:', username)
            return jsonify({'error': 'Username is already in use'}), 400

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Create a new user
        new_user = Users(firstName=first_name, lastName=last_name, username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        print('New user created:', new_user)

        return jsonify(new_user), 201
    except Exception as e:
        print('Error during signup:', traceback.format_exc())  # Log the traceback
        return jsonify({'error': 'Internal server error'}), 500

# Signin route
@auth_bp.route('/signin', methods=['POST'])
def signin():
    try:
        data = request.get_json()
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        print('Sign-in attempt:', {'email': email, 'username': username})

        # Search the Users table
        search_criteria = {'email': email} if email else {'username': username}
        user = Users.query.filter_by(**search_criteria).first()  # Make sure this refers to Users

        if not user:
            print('User not found')
            return jsonify({'error': 'Invalid credentials'}), 400

        # Compare password
        if not bcrypt.check_password_hash(user.password, password):
            print('Password mismatch')
            return jsonify({'error': 'Invalid credentials'}), 400

        token = jwt.encode({'id': user.id}, os.getenv('JWT_SECRET'), algorithm='HS256')
        return jsonify({'token': token}), 200
    except Exception as e:
        print('Internal server error:', e)
        return jsonify({'error': 'Internal server error'}), 500  