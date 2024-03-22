from flask import Blueprint, request, jsonify
from app.bots.multi_bot.multi_bot import activate_ip_bot
from app.services.coingecko.actions import get_list_of_coins
from config import Token, session

multi_bot_bp = Blueprint('multi_bot', __name__)

# Activates the Bot
@multi_bot_bp.route('/activate/ip_bot', methods=['POST'])
def ip_bot():
    try:
        token_name = request.args.get('token_name')
        analysis_prompt = request.args.get('analysis_prompt', None)

        if not token_name:
            return jsonify({'response': 'Token name is required', 'success': False}), 400
        
        result = activate_ip_bot(token_name, analysis_prompt)
        if result['success']:
            return jsonify({'response': result, 'success': True}), 200
        return jsonify({'response': result['response'], 'success': False}), 404
    except Exception as e:
        return jsonify({'response': str(e), 'success': False}), 500


# Get the ID of the token from CoinGecko
@multi_bot_bp.route('/search/token', methods=['POST'])
def get_token():
    try:
        data = request.json

        if not data:
            return jsonify({'response': 'Data is required', 'success': False}), 400

        token_name = data.get('token_name', None)
        token_symbol = data.get('token_symbol', None)
        watchlist = data.get('watchlist', False)

        if not token_name or not token_symbol:
            return jsonify({'response': 'Token name and symbol are required', 'success': False}), 400
        
        if watchlist and watchlist is not isinstance(watchlist, bool):
            return jsonify({'response': 'watchlist must be a boolean value', 'success': False}), 400
        
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
                if watchlist == True:
                    found_token_data = session.query(Token).filter_by(gecko_id=found_token['token_id']).first()
                
                    if not found_token_data:
                        new_token=Token(
                            tokenname=found_token['token_name'],
                            symbol=found_token['token_symbol'],
                            gecko_id=found_token['token_id'],
                        )
                        session.add(new_token)
                        session.commit()
                       
                        final_response['saved_to_db'] = "Token added to watchlist"
                    else:
                        final_response['saved_to_db'] = "Token already exist"

                return jsonify(final_response), 200
            else:
                return jsonify({'response': 'Token not found', 'success': False}), 404
        else:
            return jsonify({'response': response.get('response', 'Unknown error'), 'success': False}), 500
    except Exception as e:
        return jsonify({'response': str(e), 'success': False}), 500
    










# @index_bp.route('/index/activate', methods=['POST'])
# def activate_index_bot():
#     try:
#         sh_url = request.get_json()

#         if not sh_url:
#             return jsonify({'message': 'Google sheets URL expected', 'status': 404}), 404
        
#         # coins, coins_status = get_spreadsheet_coinsV2(sh_url=sh_url)
        
#         # if coins_status != 200:
#         #     return jsonify({'message': coins, 'status': 404}), 404
        
#         # get_once(coins, sh_url)
#         # get_once_a_day(coins, sh_url)
#         # get_once_a_month(coins, sh_url)
                   
#         # scheduler.add_job(get_once, run_date=datetime.now(), id=f'{sh_url + str(0)}',  args=[coins, sh_url])
#         # scheduler.add_job(get_once_a_day, 'interval', id=f'{sh_url + str(1)}', days=1, args=[coins, sh_url], next_run_time=datetime.now(), replace_existing=True)
#         # scheduler.add_job(get_once_a_month, 'interval', id=f'{sh_url + str(2)}', days=30, args=[coins, sh_url], next_run_time=datetime.now(), replace_existing=True)
  
#         jobs = scheduler.get_jobs()
#         jobs_data = [job.id[:-1] for job in jobs]
        
#         unique_items = list(set(jobs_data))
#         activation_date = "Activation date: " + str(datetime.now())

#         formatted_items = [f"{activation_date}\nSpreadsheet URL: {url}" for url in unique_items]
#         result = '\n\n'.join(formatted_items)

#         return jsonify({'message': f'{result}', 'status': 200}), 200

#     except Exception as e:
#         print(str(e))
#         return jsonify({'message': f'Error activating spreadsheet, {str(e)}', 'status': 500}), 500
    

# @index_bp.route('/index/deactivate', methods=['POST'])
# def deactivate_index_bot():
#     try:
#         sh_url = request.get_json()

#         if not sh_url:
#             return jsonify({'message': 'Google sheets URL expected', 'status': 404}), 404
        
#         for i in range(2):
#             index = i + 1
#             scheduler.remove_job(f'{sh_url + str(index)}') 

#         jobs = scheduler.get_jobs()
#         jobs_data = [job.id[:-1] for job in jobs]
        
#         unique_items = list(set(jobs_data))
#         activation_date = "Activation date: " + str(datetime.now())

#         formatted_items = [f"{activation_date}\nSpreadsheet URL: {url}" for url in unique_items]
#         result = '\n\n'.join(formatted_items)

#         return jsonify({'message': f'{result}', 'status': 200}), 200
    
#     except JobLookupError as e:
#         return jsonify({'message': 'No spreadsheet was found', 'status': 500}), 500
    
#     except Exception as e:
#         return jsonify({'message': f'Error while deactivating Index Bot: {str(e)}', 'status': 500}), 500