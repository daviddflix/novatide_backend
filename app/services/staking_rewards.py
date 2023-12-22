# Stacking Rewards Service

import os
import math
import requests
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

BASE_URL = "https://api.stakingrewards.com/public/query"
api_key = os.getenv("STAKING_REWARD_API_KEY")


def get_staking_reward_data(symbol):

  try:
      
      symbol = str(symbol).upper()

      query = f"""
        query {{
          assets(where: {{ symbols: ["{symbol}"] }}, limit: 1) {{
            name
            slug
            metrics(where: {{ metricKeys: ["reward_rate"] }}, limit: 1) {{
              metricKey
              label
              defaultValue
            }}
          }}
        }}
      """

      headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_key,
      }

      data = {"query": query}

      response = requests.post(BASE_URL, json=data, headers=headers)

      if response.status_code == 200:

        result = response.json()
        default_reward_rate = result['data']['assets'][0]['metrics'][0]['defaultValue']
        reward_rate = math.floor(default_reward_rate * 100) / 100
        formatted_reward_rate = "{:.2f}".format(reward_rate)
        
        return (f"{formatted_reward_rate}%"), 200
      else:
        return response.content, response.status_code
      
  except Exception as e:
     return f'Error getting staking reward data {str(e)}', 500
  
