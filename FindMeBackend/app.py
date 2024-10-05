from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import Config
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import logging

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

# Configure logging to write errors to error.txt
logging.basicConfig(filename='error.txt', level=logging.ERROR, format='%(asctime)s %(levelname)s: %(message)s')

# User model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

# UserLocation model
class UserLocation(db.Model):
    __tablename__ = 'user_location'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# LocationShare model
class LocationShare(db.Model):
    __tablename__ = 'location_share'
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    following_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('follower_id', 'following_id', name='_follower_following_uc'),)

# Route to create a new user
@app.route('/user', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return jsonify({"error": "Missing required fields: username, email, password"}), 400

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            return jsonify({"error": "Username or email already exists."}), 400

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "User created successfully.", "user_id": user.id}), 201
    except IntegrityError:
        db.session.rollback()
        logging.error('IntegrityError in create_user: Username or email already exists.')
        return jsonify({"error": "Username or email already exists."}), 400
    except Exception as e:
        db.session.rollback()
        logging.error(f'Exception in create_user: {str(e)}')
        return jsonify({"error": str(e)}), 400

# Route to update an existing user
@app.route('/user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return jsonify({"error": "Missing required fields: username, email, password"}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found."}), 404

        existing_user = User.query.filter(
            ((User.username == username) | (User.email == email)) & (User.id != user_id)
        ).first()
        if existing_user:
            return jsonify({"error": "Username or email already exists."}), 400

        user.username = username
        user.email = email
        user.set_password(password)
        db.session.commit()

        return jsonify({"message": "User updated successfully."}), 200
    except IntegrityError:
        db.session.rollback()
        logging.error('IntegrityError in update_user: Username or email already exists.')
        return jsonify({"error": "Username or email already exists."}), 400
    except Exception as e:
        db.session.rollback()
        logging.error(f'Exception in update_user: {str(e)}')
        return jsonify({"error": str(e)}), 400

# Route to add or update a user's location
@app.route('/location', methods=['POST'])
def add_or_update_location():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        if not user_id or latitude is None or longitude is None:
            return jsonify({"error": "Missing required fields: user_id, latitude, longitude"}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User not found."}), 404

        location = UserLocation.query.filter_by(user_id=user_id).first()
        if location:
            location.latitude = latitude
            location.longitude = longitude
            location.updated_at = datetime.utcnow()
        else:
            location = UserLocation(user_id=user_id, latitude=latitude, longitude=longitude)
            db.session.add(location)
        db.session.commit()

        return jsonify({"message": "Location updated successfully."}), 200
    except IntegrityError:
        db.session.rollback()
        logging.error('IntegrityError in add_or_update_location: Error updating location.')
        return jsonify({"error": "Error updating location."}), 400
    except Exception as e:
        db.session.rollback()
        logging.error(f'Exception in add_or_update_location: {str(e)}')
        return jsonify({"error": str(e)}), 400

# Route to get a user's location
@app.route('/location/<int:user_id>', methods=['GET'])
def get_location(user_id):
    try:
        location = UserLocation.query.filter_by(user_id=user_id).first()
        if location:
            return jsonify({
                "user_id": location.user_id,
                "latitude": location.latitude,
                "longitude": location.longitude,
                "updated_at": location.updated_at.isoformat()
            }), 200
        else:
            return jsonify({"message": "Location not found."}), 404
    except Exception as e:
        logging.error(f'Exception in get_location: {str(e)}')
        return jsonify({"error": str(e)}), 400

# Route to create or update a location share
@app.route('/location_share', methods=['POST'])
def update_location_share():
    try:
        data = request.get_json()
        follower_id = data.get('follower_id')
        following_id = data.get('following_id')
        is_approved = data.get('is_approved')

        if not follower_id or not following_id:
            return jsonify({"error": "Missing required fields: follower_id, following_id"}), 400

        if follower_id == following_id:
            return jsonify({"error": "A user cannot follow themselves."}), 400

        follower = User.query.get(follower_id)
        following = User.query.get(following_id)

        if not follower or not following:
            return jsonify({"error": "Follower or following user not found."}), 404

        location_share = LocationShare.query.filter_by(follower_id=follower_id, following_id=following_id).first()
        if location_share:
            if is_approved is not None:
                location_share.is_approved = is_approved
                db.session.commit()
                return jsonify({"message": "Location share updated successfully."}), 200
            else:
                return jsonify({"error": "Location share already exists."}), 400
        else:
            location_share = LocationShare(
                follower_id=follower_id,
                following_id=following_id,
                is_approved=is_approved
            )
            db.session.add(location_share)
            db.session.commit()
            return jsonify({"message": "Location share created successfully."}), 201
    except IntegrityError:
        db.session.rollback()
        logging.error('IntegrityError in update_location_share: Location share already exists.')
        return jsonify({"error": "Location share already exists."}), 400
    except Exception as e:
        db.session.rollback()
        logging.error(f'Exception in update_location_share: {str(e)}')
        return jsonify({"error": str(e)}), 400

# Route to get all users
@app.route('/users', methods=['GET'])
def get_users():
    try:
        users = User.query.all()
        users_data = [{
            "id": user.id,
            "username": user.username,
            "email": user.email
        } for user in users]
        return jsonify(users_data), 200
    except Exception as e:
        logging.error(f'Exception in get_users: {str(e)}')
        return jsonify({"error": str(e)}), 400

# Route to get all location shares
@app.route('/location_shares', methods=['GET'])
def get_location_shares():
    try:
        shares = LocationShare.query.all()
        shares_data = [{
            "id": share.id,
            "follower_id": share.follower_id,
            "following_id": share.following_id,
            "is_approved": share.is_approved,
            "created_at": share.created_at.isoformat()
        } for share in shares]
        return jsonify(shares_data), 200
    except Exception as e:
        logging.error(f'Exception in get_location_shares: {str(e)}')
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
