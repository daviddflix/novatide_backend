import json
from flask import Blueprint
from datetime import datetime
from app.scheduler import scheduler
from app.routes.FA_Bot.introduction import introduction, fetch_and_write_introduction_data
from app.routes.FA_Bot.tokenomics import ( 
                                        fetch_max_supply, 
                                        fetch_tokenomics_data, 
                                        get_staking_rewards_data,
                                        token_distribution_and_accrual_mechanism
                                        )

fa_bp = Blueprint('main', __name__)

# Gets the JSON containing all the coins
def get_coins():
    coins = []

    try:
        with open('app/services/spreadsheets.json', 'r') as file:
            data = json.load(file)
            for entry in data:
                id = entry["id"]
                sh_url = entry["sh_url"]
                symbol = entry["symbol"]
                competitors = entry["competitors"]
                coins.append((id, sh_url, symbol, competitors))
            
            return coins, 200

    except Exception as e:
        return f'Error getting data from spreadsheets.json {str(e)}', 500
    

# Activates the FA BOT
@fa_bp.route('/fa/activate', methods=['POST'])
def activate_fa_bot():
    try:
        coins, status = get_coins()

        if status != 200:
            return coins, status
        
        if status == 200:
            for coin in coins:
                id, sh_url, symbol_id, competitors = coin 

                scheduler.add_job(introduction, 'date', id=f'{id} Introduction', run_date=datetime.now(), args=[id, sh_url])
                scheduler.add_job(fetch_and_write_introduction_data, 'interval', id=f'{id} Introduction data', minutes=2, args=[id, sh_url], next_run_time=datetime.now())
                scheduler.add_job(fetch_max_supply, 'interval', id=f'{id} max supply', weeks=4, args=[id, sh_url], next_run_time=datetime.now())
                scheduler.add_job(fetch_tokenomics_data, 'interval', id=f'{id} token data', weeks=1, args=[id, sh_url], next_run_time=datetime.now())
                scheduler.add_job(get_staking_rewards_data, 'interval', id=f'{symbol_id} staking reward', days=1, args=[symbol_id, sh_url], next_run_time=datetime.now())
                scheduler.add_job(token_distribution_and_accrual_mechanism, 'interval', id=f'{id} token distribution', weeks=24, args=[id, sh_url], next_run_time=datetime.now())
                
                # fetch and write data to the feature section column 3 and 4
                for index, competitor in enumerate(competitors):
                    column = index + 3
                    competitor_id, symbol = competitor["id"], competitor["symbol"]
                    scheduler.add_job(fetch_max_supply, 'interval', id=f'{competitor_id} max supply', weeks=4, args=[competitor_id, sh_url, column], next_run_time=datetime.now())
                    scheduler.add_job(fetch_tokenomics_data, 'interval', id=f'{competitor_id} token data', weeks=1, args=[competitor_id, sh_url, column], next_run_time=datetime.now())

                print(f'FA Bot activated for {id}')

            return f'All FA Bot activated', 200
            
    except Exception as e:
        return f'An error occured activating FA Bot: {str(e)}', 500
    

# Deactivates 
@fa_bp.route('/fa/deactivate', methods=['POST'])
def deactivate_fa_bot():
    try:
        
        scheduler.remove_all_jobs()
        return 'All FA Bot deactivated', 200
        
    except Exception as e:
        return f'Error while deactivating FA Bot: {str(e)}', 500




