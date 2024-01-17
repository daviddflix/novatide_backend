import requests
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()
COINMARKET_API_KEY = os.getenv("COINMARKET_API_KEY")

def get_crypto_metadata(coin_name):

    base_url = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/info"
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': COINMARKET_API_KEY,
    }

    formatted_coin = str(coin_name).upper()

    params = {
        'symbol': formatted_coin,
    }

    try:
        response = requests.get(base_url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'data' in data and formatted_coin in data['data']:
                urls = data['data'][formatted_coin][0]['urls']
                if 'technical_doc' in urls and urls['technical_doc']:
                    return urls['technical_doc'][0]
            else:
                print(f"Error: No technical documentation URL found for {formatted_coin}.")
                return None
        else:
            print(f"Error: Unable to retrieve metadata for {formatted_coin}. Check the coin symbol.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None


# coin_name = 'dbc'

# metadata = get_crypto_metadata(coin_name)

# print(metadata)
