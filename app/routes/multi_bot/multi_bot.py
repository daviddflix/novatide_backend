from flask import Blueprint, request, jsonify
from app.bots.multi_bot.multi_bot import get_all_available_data, activate_multi_bot
from app.services.CoinGecko.actions import get_list_of_coins
from config import Token, session, Watchlist, Session, Bot
from app.scheduler import scheduler
from datetime import datetime
from sqlalchemy import or_

multi_bot_bp = Blueprint('multi_bot', __name__)

# Get all available data
@multi_bot_bp.route('/activate/multi_bot', methods=['POST'])
def get_data_tokens():
    try:
        token_name = request.args.get('token_name')
        analysis_prompt = request.args.get('analysis_prompt', None)

        if not token_name:
            return jsonify({'response': 'Token name is required', 'success': False}), 400
        
        result = get_all_available_data(token_name, analysis_prompt)
        if result['success']:
            return jsonify({'response': result, 'success': True}), 200
        return jsonify({'response': result['response'], 'success': False}), 404
    except Exception as e:
        return jsonify({'response': str(e), 'success': False}), 500


# Activates the BOT
@multi_bot_bp.route('/multi-bot', methods=['POST'])
def ip_bot():
    try:
        command = request.args.get('command')
        bot_id = request.args.get('bot_id')

        if not command or not bot_id:
            return jsonify({'response': 'Command and bot ID are required', 'success': False}), 400
        
        with Session() as session:
            bot = session.query(Bot).filter(Bot.id == bot_id).first()
        
            if command == 'activate':
                if bot.status:
                    return jsonify({'response': f'{bot.name} bot is already active', 'success': False}), 400
            
                bot.status = True
                session.commit()
                scheduler.add_job(activate_multi_bot, 'interval', 
                                  minutes=bot.interval, id=bot.name, 
                                  replace_existing=True, 
                                  max_instances=2)

                return jsonify({'response': 'Bot activated', 'success': True}), 200
            elif command == 'deactivate':
                if not bot.status:
                    return jsonify({'response': f'{bot.name} bot is already deactivated', 'success': False}), 400
                
                scheduler.remove_job(bot.name)
                bot.status = False
                session.commit()
                
                return jsonify({'response': 'Bot deactivated', 'success': True}), 200
            else:
                return jsonify({'response': 'Command not valid', 'success': False}), 400
    except Exception as e:
        return jsonify({'response': str(e), 'success': False}), 500

# activate_multi_bot()
 #   next_run_time=datetime.now(),

 # Get all existing bots.
@multi_bot_bp.route('/bots', methods=['GET'])
def get_bots():
    try:
        with Session() as session:
            bots = session.query(Bot).all()
            bot_list = []

            for bot in bots:
                bot_dict = bot.as_dict()
                job = scheduler.get_job(bot.name)
                bot_dict['next_run_time'] = None
                if job:
                    bot_dict['next_run_time'] = job.next_run_time
                bot_list.append(bot_dict)

            return jsonify({'bots': bot_list}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    

@multi_bot_bp.route('/multi-bot/edit-interval', methods=['POST'])
def edit_interval():
    try:
        bot_id = request.args.get('bot_id')
        new_interval = request.args.get('interval')

        if not bot_id or not new_interval:
            return jsonify({'response': 'Bot ID and new interval are required', 'success': False}), 400

        # Check if the new interval is not negative
        if int(new_interval) < 0:
            return jsonify({'response': 'Interval cannot be negative', 'success': False}), 400

        with Session() as session:
            bot = session.query(Bot).filter(Bot.id == bot_id).first()

            if not bot:
                return jsonify({'response': 'Bot not found', 'success': False}), 404

            bot.interval = int(new_interval)
            session.commit()

            # Reschedule the job with the new interval
            job = scheduler.get_job(bot.name)
            if job:
                scheduler.reschedule_job(job.id, trigger='interval', hours=bot.interval)
                return jsonify({'response': 'Interval updated and job rescheduled', 'success': True}), 200
            else:
                return jsonify({'response': f'{bot.name} bot is not active yet, please activate first', 'success': False}), 400
    except Exception as e:
        return jsonify({'response': str(e), 'success': False}), 500



# Get the ID of the token from CoinGecko and add the token to a watchlist if specified.
@multi_bot_bp.route('/search/token', methods=['POST'])
def get_token():
    try:
        data = request.json

        if not data:
            return jsonify({'response': 'Data is required', 'success': False}), 400

        token_name = data.get('token_name', None)
        token_symbol = data.get('token_symbol', '')
        watchlist_name = data.get('watchlist', None)

        if not token_name:
            return jsonify({'response': 'Token name is required', 'success': False}), 400
        
        
        response = get_list_of_coins()
        if response['success']:
            found_token = None

            tokens = response['list_all_tokens']

            formatted_token_name = str(token_name).casefold().strip()
            formatted_token_symbol = str(token_symbol).casefold().strip()
            for token in tokens:
                if str(token['name']).casefold() == formatted_token_name and str(token['symbol']).casefold() == formatted_token_symbol:
                    found_token = {
                        'token_id': token['id'],
                        'token_symbol': token['symbol'],
                        'token_name': token['name'],
                    }
                    break
            
            if found_token:
                final_response = {'response': found_token, 'success': True}
                if watchlist_name:
                    found_token_data = session.query(Token).filter_by(gecko_id=found_token['token_id']).first()
                    watchlist = session.query(Watchlist).filter_by(name=watchlist_name).first()

                    if watchlist and not found_token_data:
                        new_token=Token(
                            tokenname=found_token['token_name'],
                            symbol=found_token['token_symbol'],
                            gecko_id=found_token['token_id'],
                        )
                        watchlist.tokens.append(new_token)
                        session.add(new_token)
                        session.commit()
                    
                        final_response['saved_to_db'] = "Token added to watchlist"
                    else:
                        final_response['saved_to_db'] = "Token already exist"
                        
                    return jsonify(final_response), 200
                else:
                    return jsonify(final_response), 200
            else:
                return jsonify({'response': 'Token not found', 'success': False}), 404
        else:
            return jsonify({'response': response.get('response', 'Unknown error'), 'success': False}), 500
    except Exception as e:
        session.rollback()
        return jsonify({'response': str(e), 'success': False}), 500
        
    

# Get tokens data
@multi_bot_bp.route('/get/tokens', methods=['GET'])
def get_all_tokens():
    try:
        tokens = session.query(Token).order_by(Token.created_at).all()
        serialized_tokens = [token.as_dict() for token in tokens]
        return jsonify({'response': serialized_tokens, 'success': True}), 200
    
    except Exception as e:
        # If an exception occurs, return an error response
        return jsonify({'response': str(e), 'success': False}), 500
    


# Delete tokens
@multi_bot_bp.route('/delete/tokens', methods=['DELETE'])
def delete_tokens():
    try:
        if not request.json or 'ids' not in request.json:
            return jsonify({'response': 'No JSON data or IDs provided', 'success': False}), 400
        
        ids = request.json['ids']
        
        # Check if the IDs array is empty
        if not ids:
            return jsonify({'response': 'IDs array is empty', 'success': False}), 400
        
        # Delete tokens with the specified IDs
        for token_id in ids:
            token = session.query(Token).get(token_id)
            if token:
                # Remove associations first
                for watchlist in token.watchlists:
                    watchlist.tokens.remove(token)
                # Then delete the token
                session.delete(token)
        
        session.commit()
        
        return jsonify({'response': f'{len(ids)} tokens deleted successfully', 'success': True}), 200
    
    except Exception as e:
        session.rollback()
        print(e)
        return jsonify({'response': str(e), 'success': False}), 500
