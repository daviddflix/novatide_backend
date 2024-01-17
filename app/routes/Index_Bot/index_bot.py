import os
import gspread
import logging
from flask import jsonify
from datetime import datetime
from gspread.cell import Cell
from dotenv import load_dotenv
from itertools import zip_longest 
from app.scheduler import scheduler
from flask import Blueprint, request
from apscheduler.jobstores.base import JobLookupError
from app.services.coingecko import get_list_of_coins
from app.routes.Index_Bot.api_data import get_once, get_once_a_day, get_once_a_month


gc = gspread.service_account(filename='app\\services\\service_account.json')

index_bp = Blueprint('index', __name__)

# Set up logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Load environment variables from the .env file
load_dotenv()

BASE_URL = 'https://pro-api.coingecko.com/api/v3'
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")


    
# Updates a single cell
def update_cell(cell, worksheet, message="Coin not found. Looking for more data..."):
    try:
        cell_list = [
            Cell(cell, 3, message)
            ]
            
        worksheet.update_cells(cell_list)
        return f'Cell {cell} updated', 200
    
    except gspread.exceptions.APIError as e:
        return 'Error accessing Google Sheets API', 500

    except Exception as e:
        return 'Error updating cell', 500


# Gets all the coins in the spreadsheet in a single list
def get_spreadsheet_coinsV2(sh_url):
    try:
        sh = gc.open_by_url(url=sh_url)
        worksheet = sh.get_worksheet(0)

        coins_list = worksheet.col_values(1)
        coins_symbols = worksheet.col_values(2)

        if coins_list and coins_symbols:

            list_of_coins, status = get_list_of_coins()
          
            if status == 200:
                coins_dict = zip_longest(coins_list[1:], coins_symbols[1:], fillvalue='NA')

                result_dict_coins = []
                for coin_name, coin_symbol in coins_dict:
                    if coin_symbol == '':
                        coin_symbol = 'NA'

                    for coin in list_of_coins:
                        if coin_name.casefold() == coin['name'].casefold():
                            coin_name = coin['id']
                            break
                        elif coin_name.casefold() == coin['id'].casefold():
                            break
                       
                    result_dict_coins.append({'coin_id': coin_name.casefold(), 'coin_symbol': coin_symbol.casefold()})

                return result_dict_coins, 200
            else:
                return 'Error while getting coins from Coingecko', 404
        else:
            return 'No coins were found in the spreadsheet', 404

    except gspread.exceptions.APIError as e:
        return f'Error accessing Google Sheets API - {str(e)}', 500

    except Exception as e:
        return f'Error getting coins - {str(e)}', 500



@index_bp.route('/index/activate', methods=['POST'])
def activate_index_bot():
    try:
        sh_url = request.get_json()

        if not sh_url:
            return jsonify({'message': 'Google sheets URL expected', 'status': 404}), 404
        
        coins, coins_status = get_spreadsheet_coinsV2(sh_url=sh_url)
        
        if coins_status != 200:
            return jsonify({'message': coins, 'status': 404}), 404
                   
        scheduler.add_job(get_once, run_date=datetime.now(), id=f'{sh_url + str(0)}',  args=[coins, sh_url])
        scheduler.add_job(get_once_a_day, 'interval', id=f'{sh_url + str(1)}', days=1, args=[coins, sh_url], next_run_time=datetime.now(), replace_existing=True)
        scheduler.add_job(get_once_a_month, 'interval', id=f'{sh_url + str(2)}', days=30, args=[coins, sh_url], next_run_time=datetime.now(), replace_existing=True)
  
        jobs = scheduler.get_jobs()
        jobs_data = [job.id[:-1] for job in jobs]
        
        unique_items = list(set(jobs_data))
        activation_date = "Activation date: " + str(datetime.now())

        formatted_items = [f"{activation_date}\nSpreadsheet URL: {url}" for url in unique_items]
        result = '\n\n'.join(formatted_items)

        return jsonify({'message': f'{result}', 'status': 200}), 200

    except Exception as e:
        print(str(e))
        return jsonify({'message': f'Error activating spreadsheet, {str(e)}', 'status': 500}), 500
    

@index_bp.route('/index/deactivate', methods=['POST'])
def deactivate_index_bot():
    try:
        sh_url = request.get_json()

        if not sh_url:
            return jsonify({'message': 'Google sheets URL expected', 'status': 404}), 404
        
        for i in range(2):
            index = i + 1
            scheduler.remove_job(f'{sh_url + str(index)}') 

        jobs = scheduler.get_jobs()
        jobs_data = [job.id[:-1] for job in jobs]
        
        unique_items = list(set(jobs_data))
        activation_date = "Activation date: " + str(datetime.now())

        formatted_items = [f"{activation_date}\nSpreadsheet URL: {url}" for url in unique_items]
        result = '\n\n'.join(formatted_items)

        return jsonify({'message': f'{result}', 'status': 200}), 200
    
    except JobLookupError as e:
        return jsonify({'message': 'No spreadsheet was found', 'status': 500}), 500
    
    except Exception as e:
        return jsonify({'message': f'Error while deactivating Index Bot: {str(e)}', 'status': 500}), 500
    


