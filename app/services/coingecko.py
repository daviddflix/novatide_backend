# CoinGecko Service

import math
import requests

BASE_URL = 'https://api.coingecko.com/api/v3'


def calculate_percentage(part, total):
    percentage = (part / total) * 100
    percentage_floor = math.floor(percentage)
    return f"{percentage_floor}%"


def fetch_tokenomics_data(coin):

    try:
        response = requests.get(f'{BASE_URL}/coins/{coin}')
        response.raise_for_status()
        
        if response.status_code == 200:
            response = response.json()
            market_data = response.get('market_data')
            
            total_supply = 'No data found' if market_data['total_supply'] is None else market_data['total_supply']
            max_supply = 'Infinite' if market_data['max_supply'] is None else market_data['max_supply']
            circulating_supply = market_data['circulating_supply']
            last_updated = market_data['last_updated']

            supply_model = 'Deflationary'

            if max_supply == 'Infinite':
                supply_model = 'Inflationary'

            circulating_supply_percentaje = '100%'

            if max_supply != 'Infinite' and circulating_supply:
                percentage = calculate_percentage(part=circulating_supply, total=max_supply)
                circulating_supply_percentaje = percentage

             
            return (total_supply, max_supply, circulating_supply, 
                    circulating_supply_percentaje, supply_model, last_updated), 200
        
    except Exception as e:
        return f'Error fetching tokenomics data: {str(e)}', 500
    


def fetch_introduction_data(coin):

    try:
        response = requests.get(f'{BASE_URL}/simple/price?ids={coin}&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true&include_last_updated_at=true')
        response.raise_for_status()
     
        if response.status_code == 200:
            response_json = response.json()
            coin_data = response_json.get(coin, {})

            usd_market_cap = coin_data.get('usd_market_cap', 'No data found')
            usd_24h_vol = coin_data.get('usd_24h_vol', 'No data found')

            return (usd_market_cap, usd_24h_vol), 200


    except Exception as e:
        return f'Error fetching introduction data: {str(e)}', 500 
