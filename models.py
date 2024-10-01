from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import TIMESTAMP

db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = 'Users'  # Use the exact table name

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Auto-incrementing primary key
    firstName = db.Column(db.String(255), nullable=False)  # First name with a maximum length of 255
    lastName = db.Column(db.String(255), nullable=False)  # Last name with a maximum length of 255
    username = db.Column(db.String(100), unique=True, nullable=False)  # Unique username with a maximum length of 100
    email = db.Column(db.String(255), unique=True, nullable=False)  # Unique email with a maximum length of 255
    password = db.Column(db.Text, nullable=False)  # Password, using Text for longer storage
    createdAt = db.Column(TIMESTAMP(timezone=True), server_default=db.func.current_timestamp())  # Creation timestamp
    updatedAt = db.Column(TIMESTAMP(timezone=True), server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())  # Update timestamp
    reviewCount = db.Column(db.Integer, default=0)  # Review count defaulting to 0
    exp = db.Column(db.Integer, default=0)  # Experience points defaulting to 0
    level = db.Column(db.String)  # Level type, adjust if you have a specific level_type definition
     
    def to_dict(self):
        """Convert the user object to a dictionary."""
        return {
            'id': self.id,
            'firstName': self.firstName,
            'lastName': self.lastName,
            'username': self.username,
            'email': self.email,
            'reviewCount': self.reviewCount,
            'exp': self.exp,
            'level': self.level,
            'createdAt': self.createdAt,
            'updatedAt': self.updatedAt,
            # Do not include the password in the response for security reasons
        }
class Game(db.Model):
    __tablename__ = 'games'  # Name of the table

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Auto-incrementing primary key
    name = db.Column(db.String(255), nullable=False, unique=True)  # Game name with unique constraint
    normalized_name = db.Column(db.String(255), nullable=False, unique=True)  # Normalized game name with unique constraint
    cover = db.Column(db.Text)  # Cover image URL or data
    description = db.Column(db.Text)  # Game description
    created_at = db.Column(TIMESTAMP(timezone=False), server_default=db.func.current_timestamp())  # Creation timestamp
    updated_at = db.Column(TIMESTAMP(timezone=False), server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())  # Update timestamp

    def __repr__(self):
        return f"<Game {self.name}>"

    def to_dict(self):
        """Convert the game object to a dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'normalized_name': self.normalized_name,
            'cover': self.cover,
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, nullable=False)
    game_name = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    review = db.Column(db.Text, nullable=False)
    time_spent = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'game_id': self.game_id,
            'game_name': self.game_name,
            'user_id': self.user_id,
            'review': self.review,
            'time_spent': self.time_spent,
            'rating': self.rating,
            'date': self.date.isoformat()
        }

class ReviewInfo(db.Model):
    __tablename__ = 'review_info'

    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.id'), nullable=False)
    high = db.Column(db.String, nullable=False)
    low = db.Column(db.String, nullable=False)
    atmosphere = db.Column(db.Integer, nullable=False)
    story = db.Column(db.Integer, nullable=False)
    dev_note = db.Column(db.String, nullable=False)
    gameplay = db.Column(db.Integer, nullable=False)
    difficulty = db.Column(db.Integer, nullable=False)

    def serialize(self):
        return {
            'id': self.id,
            'review_id': self.review_id,
            'high': self.high,
            'low': self.low,
            'atmosphere': self.atmosphere,
            'story': self.story,
            'dev_note': self.dev_note,
            'gameplay': self.gameplay,
            'difficulty': self.difficulty
        }
class Friends(db.Model):
    __tablename__ = 'friends'  # Use the exact table name

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Auto-incrementing primary key
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))  # Foreign key referencing Users
    friend_id = db.Column(db.Integer, db.ForeignKey('Users.id'))  # Foreign key referencing Users
    status = db.Column(db.String(10), default='pending')  # Default status is 'pending'
    created_at = db.Column(TIMESTAMP(timezone=False), server_default=db.func.now())  # Creation timestamp

    # Define relationships (optional, but useful for ORM)
    user = db.relationship('Users', foreign_keys=[user_id], backref='user_friends')  # User who sent the request
    friend = db.relationship('Users', foreign_keys=[friend_id], backref='friends')  # User who received the request

    def to_dict(self):
        """Convert the friend object to a dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'friend_id': self.friend_id,
            'status': self.status,
            'created_at': self.created_at,
        }