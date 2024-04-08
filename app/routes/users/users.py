from flask import Blueprint, request, jsonify
from config import Session, User
from datetime import datetime

users_bp = Blueprint('users', __name__)

@users_bp.route('/create_user', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')

        if not username or not email or not password or not role:
            return jsonify({'error': 'Please provide username, email, role and password'}), 400

        with Session() as session:
            # Check if the username or email already exists
            existing_user_username = session.query(User).filter_by(username=username).first()
            existing_user_email = session.query(User).filter_by(email=email).first()
            if existing_user_username:
                return jsonify({'error': 'Username already exists'}), 400
            if existing_user_email:
                return jsonify({'error': 'Email already registered'}), 400

            new_user = User(
                username=username,
                email=email,
                password_hash=password,
                role=role,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

            session.add(new_user)
            session.commit()
            

            return jsonify({'message': 'User created successfully'}), 201
    
    except Exception as e:
        with Session() as session:
            session.rollback()
        return jsonify({'error': str(e)}), 500


@users_bp.route('/delete_user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        with Session() as session:
            user = session.query(User).filter_by(id=user_id).first()

            if not user:
                return jsonify({'error': 'User not found'}), 404

            session.delete(user)
            session.commit()

            return jsonify({'message': 'User deleted successfully'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

# Get all users
@users_bp.route('/get_all_users', methods=['GET'])
def get_all_users():
    try:
        with Session() as session:
            users = session.query(User).all()
            user_list = [user.as_dict() for user in users]
            return jsonify({'users': user_list}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


    
@users_bp.route('/users/<int:user_id>/change_password', methods=['PUT'])
def change_password(user_id):
    try:
        data = request.get_json()
        new_password = data.get('new_password')

        if not new_password:
            return jsonify({'error': 'Please provide a new password'}), 400

        with Session() as session:
            # Check if the user exists
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                return jsonify({'error': 'User not found'}), 404

            # Update the password and update the updated_at field
            user.password_hash = new_password
            user.updated_at = datetime.now()

            session.commit()

            return jsonify({'message': 'Password changed successfully'}), 200
    
    except Exception as e:
        with Session() as session:
            session.rollback()
        return jsonify({'error': str(e)}), 500
