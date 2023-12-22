import json
from flask import Blueprint
from app.services.staking_rewards import get_staking_reward_data
from app.services.coingecko import fetch_tokenomics_data, fetch_introduction_data
from app.services.spreadsheet import write_data_to_tokenomics_feature_section, write_data_to_tokenomics_mechanism_section, write_data_to_introduction_section

fa_bp = Blueprint('main', __name__)

@fa_bp.route('/fetch', methods=['GET'])
def get_data_from_apis():

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

    except Exception as e:
        return f'Error getting data from spreadsheets.json {str(e)}', 500
    
    try:

        for coin in coins:
            id, sh_url, symbol_id, competitors = coin

            # fetch and write data to the feature section column 2
            api_response, api_status = fetch_tokenomics_data(coin=id)
            print('\napi_response: ', api_response)

            if api_status == 200:
                feature_response_2 = write_data_to_tokenomics_feature_section(sh_url=sh_url, column=2, data=api_response)
                print('\nfeature_response_2: ', feature_response_2)

             # fetch and write data to the feature section column 3 and 4
            for index, competitor in enumerate(competitors):
                column = index + 3
                competitor_id, symbol = competitor["id"], competitor["symbol"]
                competitor_response, competitor_status = fetch_tokenomics_data(coin=competitor_id)

                print('\ncompetitor_response: ', competitor_response)
                if competitor_status == 200:
                    feature_response = write_data_to_tokenomics_feature_section(sh_url=sh_url, column=column, data=competitor_response)
                    print(f'\nfeature_response_{column}: ', feature_response)


            # get and write the monetary incentive
            staking_reward_response, sr_status = get_staking_reward_data(symbol=symbol_id)
            if sr_status == 200:
                mechanism_response = write_data_to_tokenomics_mechanism_section(sh_url=sh_url, data=staking_reward_response)
                print('\nmechanism_response: ', mechanism_response)

            # get and write the market cap and 24h volumn
            introduction_response, intro_status = fetch_introduction_data(coin=id)
            if intro_status == 200:
                response = write_data_to_introduction_section(sh_url=sh_url, data=introduction_response)
                print('\nintroduction_response: ', response)


        return 'ok', 200
            
    except Exception as e:
        return f'Error in getting data from APIs {str(e)}'