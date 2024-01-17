import os
import requests
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

BASE_URL = 'https://pro-api.coingecko.com/api/v3'
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")

headers = {
            "Content-Type": "application/json",
            "x-cg-pro-api-key": COINGECKO_API_KEY,
        }

def confirm_coin_existence(coin):
    
    formatted_coin = str(coin).casefold().strip()
    response = requests.get(f'{BASE_URL}/coins/{formatted_coin}', headers=headers)

    if response.status_code == 200:
        return True
    else:
        return False
    

# Returns a list of Dicts with all the available coins in Coingecko
def get_list_of_coins():

    try:
        coingecko_response = requests.get(f'{BASE_URL}/coins/list', headers=headers)

        if coingecko_response.status_code == 200:
            return coingecko_response.json(), coingecko_response.status_code
        
        return coingecko_response.content, coingecko_response.status_code
    except Exception as e:
        print(f"Error: {str(e)}")
        return None, None
            