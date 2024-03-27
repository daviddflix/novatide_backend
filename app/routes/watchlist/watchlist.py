from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from config import Watchlist, session
from datetime import datetime

watchlist_bp = Blueprint('watchlist', __name__)


# Creates a watchlist
@watchlist_bp.route('/create/watchlist', methods=['POST'])
def create_watchlist():
    data = request.json

    if not data:
        return jsonify({'error': 'Data is required', 'success': False}), 400

    if 'name' not in data or 'description' not in data:
        return jsonify({'error': 'Name and description are required fields', 'success': False}), 400
    
    watchlist_name = data.get('name')

    if session.query(Watchlist).filter_by(name=watchlist_name).first():
        return jsonify({'error': 'Watchlist already exist', 'success': False}), 400

    new_watchlist = Watchlist(
        name=data.get('name'),
        description=data.get('description'),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    session.add(new_watchlist)
    
    try:
        session.commit()
        return jsonify({'message': 'Watchlist created successfully', 'success': True}), 201
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e), 'success': False}), 500
 

# Deletes a watchlist
@watchlist_bp.route('/delete/watchlist/<int:watchlist_id>', methods=['DELETE'])
def delete_watchlist(watchlist_id):
    try:
        watchlist = session.query(Watchlist).filter_by(id=watchlist_id).first()

        if not watchlist:
            return jsonify({'error': 'Watchlist not found', 'success': False}), 404

        # Delete the watchlist
        session.delete(watchlist)
        session.commit()
        return jsonify({'message': 'Watchlist deleted successfully', 'success': True}), 200
    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({'error': str(e), 'success': False}), 500
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500
    finally:
        session.close()


# Get all watchlist along with their tokens
@watchlist_bp.route('/watchlists', methods=['GET'])
def get_watchlists_with_tokens():
    try:
        # Query all watchlists with their associated tokens
        watchlists = session.query(Watchlist).options((joinedload(Watchlist.tokens))).all()

        # Serialize the data
        watchlists_data = []
        for watchlist in watchlists:
            watchlist_data = watchlist.as_dict()
            watchlist_data['tokens'] = [token.as_dict() for token in watchlist.tokens]
            watchlists_data.append(watchlist_data)

        return jsonify({'watchlists': watchlists_data, 'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500
    

# Route for getting watchlists without tokens
@watchlist_bp.route('/watchlists/nontokens', methods=['GET'])
def get_watchlists_without_tokens():
    try:
        # Query all watchlists without their associated tokens
        watchlists = session.query(Watchlist).all()

        watchlists_data = [watchlist.as_dict() for watchlist in watchlists]
        return jsonify({'watchlists': watchlists_data, 'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500