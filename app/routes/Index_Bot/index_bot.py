
from dotenv import load_dotenv
from app.scheduler import scheduler
from flask import Blueprint, request
from apscheduler.jobstores.base import JobLookupError
from app.services.coingecko.actions import get_token_data
from app.services.gspread.actions import get_spreadsheet_coinsV2
from app.services.coinMarketCap.coinmarketcap import get_crypto_metadata


index_bp = Blueprint('index', __name__)

# Load environment variables from the .env file
load_dotenv()
# print(get_token_data('yield-guild-games'))
# print(get_crypto_metadata('ygg'))







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
    


