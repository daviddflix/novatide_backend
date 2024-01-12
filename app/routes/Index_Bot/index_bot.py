import os
import json
import gspread
import logging
import requests
from flask import jsonify
from datetime import datetime
from gspread.cell import Cell
from dotenv import load_dotenv 
from app.scheduler import scheduler
from flask import Blueprint, request
from app.routes.Index_Bot.api_data import get_once, get_once_a_day, get_once_a_month
from app.services.coingecko import confirm_coin_existence

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
def get_spreadsheet_coins(sh_url):
    try:
        sh = gc.open_by_url(url=sh_url)
        worksheet = sh.get_worksheet(0)

        coins_list = worksheet.col_values(1)

        for index, coin in enumerate(coins_list[2:]):
            index = index + 3
            existance_coin = confirm_coin_existence(coin=coin)
            if not existance_coin:
                update_cell(cell=index, worksheet=worksheet)

        if coins_list:
            return coins_list, 200
        
        return 'No coins were found in the spreadsheet', 404

    except gspread.exceptions.APIError as e:
        return 'Error accessing Google Sheets API', 500

    except Exception as e:
        return 'Error getting coins', 500
    

@index_bp.route('/index/activate', methods=['POST'])
def activate_index_bot():
    try:
        sh_url = request.get_json()

        if not sh_url:
            return jsonify({'message': 'Google sheets URL expected', 'status': 404}), 404
        
        coins, coins_status = get_spreadsheet_coins(sh_url=sh_url)
        
        if coins_status != 200:
            return jsonify({'message': coins, 'status': 404}), 404
                   
        get_once(coins=coins, sh_url=sh_url)
        scheduler.add_job(get_once_a_day, 'interval', id=f'{sh_url + str(1)}', days=1, args=[coins, sh_url], next_run_time=datetime.now(), replace_existing=True)
        scheduler.add_job(get_once_a_month, 'interval', id=f'{sh_url + str(2)}', days=30, args=[coins, sh_url], next_run_time=datetime.now(), replace_existing=True)
  
        jobs = scheduler.get_jobs()
        jobs_data = [job.id[:-1] for job in jobs]
        
        unique_items = list(set(jobs_data))
        return jsonify({'message': f'{unique_items}', 'status': 200}), 200

    except Exception as e:
        print(str(e))
        return jsonify({'message': f'Error activating spreadsheet, {str(e)}', 'status': 500}), 500
    

@index_bp.route('/index/deactivate', methods=['POST'])
def deactivate_index_bot():
    try:
        scheduler.remove_all_jobs()
        return 'All Index Bot deactivated', 200
        
    except Exception as e:
        return f'Error while deactivating Index Bot: {str(e)}', 500
    


