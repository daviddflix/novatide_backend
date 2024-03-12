import os
import requests
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")

BASE_URL = 'https://pro-api.coingecko.com/api/v3'

headers = {
            "Content-Type": "application/json",
            "x-cg-pro-api-key": COINGECKO_API_KEY,
        }
    


            