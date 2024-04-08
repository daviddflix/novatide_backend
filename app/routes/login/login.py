from flask import Blueprint, request, jsonify
from config import Session, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Please provide username and password'}), 400

        with Session() as session: 
            user = session.query(User).filter_by(username=username).first()

            if not user or user.password_hash != password:
                return jsonify({'error': 'Invalid username or password'}), 401
            
            if user.is_active:
                return jsonify({'error': 'Another session of this user is already active. Please log out from the other session if you wish to log in here.'}), 401

            user.is_active = True
            user.is_authenticated = True
            session.commit()

            return jsonify({'message': 'User logged in successfully', 'user': user.as_dict()}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/logout', methods=['POST'])
def logout():
    try:
        data = request.get_json()
        username = data.get('username')
 
        with Session() as session:
            user = session.query(User).filter_by(username=username).first() 
            
            if user:
                user.is_active = False
                user.is_authenticated = False
                session.commit()

        return jsonify({'message': 'User logged out successfully', 'user': user.as_dict()}), 200
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

