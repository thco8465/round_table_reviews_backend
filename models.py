from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = 'Users'  # Use the exact table name
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(50))
    lastName = db.Column(db.String(50))
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(128))

    def to_dict(self):
        return {
            'id': self.id,
            'firstName': self.firstName,
            'lastName': self.lastName,
            'username': self.username,
            'email': self.email,
            # Do not include the password in the response for security reasons
        }

class Game(db.Model):
    __tablename__ = 'games'  # Name of the table

    id = db.Column(db.Integer, primary_key=True)  # Primary key
    name = db.Column(db.String(255), nullable=False)  # Game name
    normalized_name = db.Column(db.String(255), nullable=False)  # Normalized game name
    cover = db.Column(db.String(255), nullable=True)  # URL for the cover image
    description = db.Column(db.Text, nullable=True)  # Game description

    def __repr__(self):
        return f"<Game {self.name}>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'normalized_name': self.normalized_name,
            'cover': self.cover,
            'description': self.description,
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
