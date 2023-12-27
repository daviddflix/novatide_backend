import os
import math
import gspread
import requests
from gspread.cell import Cell
from dotenv import load_dotenv
from app.services.openAI import ask

# Load environment variables from the .env file
load_dotenv()

STAKING_REWARD_API_KEY = os.getenv("STAKING_REWARD_API_KEY")
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")

STAKING_REWARD_BASE_URL = "https://api.stakingrewards.com/public/query"
BASE_URL = 'https://pro-api.coingecko.com/api/v3'

gc = gspread.service_account(filename='app\\services\\service_account.json')


# Calculates the percentage of a value
def calculate_percentage(part, total):
    percentage = (part / total) * 100
    percentage_floor = math.floor(percentage)
    return f"{percentage_floor}%"


# EVERY MONTH
# Gets the max supply - supply model value for a coin
def fetch_max_supply(coin, sh_url, column=2):

    formatted_coin = str(coin).casefold()

    try:
        headers = {
        "Content-Type": "application/json",
        "x-cg-pro-api-key": COINGECKO_API_KEY,
        }

        response = requests.get(f'{BASE_URL}/coins/{formatted_coin}', headers=headers)
        response.raise_for_status()
        
        if response.status_code == 200:
            response = response.json()
            market_data = response.get('market_data')
            
            max_supply = 'Infinite' if market_data['max_supply'] is None else "{:,.2f}".format(market_data['max_supply'])
            supply_model = 'Deflationary'

            if max_supply == 'Infinite':
                supply_model = 'Inflationary'

            try:
                sh = gc.open_by_url(url=sh_url)
                worksheet = sh.get_worksheet(2)

                cell_list = [
                        Cell(7, column, max_supply),  
                        Cell(8, column, supply_model),
                    ]
        
                worksheet.update_cells(cell_list)
                return f'Max supply - supply model updated successfully for {formatted_coin}'
            
            except Exception as e:
                return f'Error writing {formatted_coin} max supply - supply model to the spreadsheet: {str(e)}'

    except Exception as e:
        return f'Error fetching max supply - supply model value: {str(e)}', 500
    

# ONCE A WEEK
# Gets the circulating supply
def fetch_tokenomics_data(coin, sh_url, column=2):

    try:

        headers = {
        "Content-Type": "application/json",
        "x-cg-pro-api-key": COINGECKO_API_KEY,
        }

        response = requests.get(f'{BASE_URL}/coins/{coin}', headers=headers)
        response.raise_for_status()
        
        if response.status_code == 200:
            response = response.json()
            market_data = response.get('market_data')
            
            total_supply = 'No data found' if market_data['total_supply'] is None else "{:,.2f}".format(market_data['total_supply'])
            max_supply = 'Infinite' if market_data['max_supply'] is None else market_data['max_supply']
            circulating_supply = market_data['circulating_supply']
            # last_updated = market_data['last_updated']

            circulating_supply_percentaje = '100%'

            if max_supply != 'Infinite' and circulating_supply:
                percentage = calculate_percentage(part=circulating_supply, total=max_supply)
                circulating_supply_percentaje = percentage

             
            try:    
                sh = gc.open_by_url(url=sh_url)
                worksheet = sh.get_worksheet(2)
            
                cell_list = [
                    Cell(4, column, total_supply),  
                    Cell(5, column, circulating_supply), 
                    Cell(6, column, circulating_supply_percentaje),    
                ]

                response = worksheet.update_cells(cell_list)
                return f'Feature section updated successfully for {coin}'
        
            except Exception as e:
                return f'Error writing data to the feature section: {str(e)}', 500
        
    except Exception as e:
        return f'Error fetching tokenomics data: {str(e)}', 500
    
# ONCE A DAY
# Stacking Rewards Service
def get_staking_rewards_data(symbol, sh_url):

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
        "X-API-KEY": STAKING_REWARD_API_KEY,
      }

      data = {"query": query}

      response = requests.post(STAKING_REWARD_BASE_URL, json=data, headers=headers)
    
      if response.status_code == 200:

        result = response.json()
        default_reward_rate = result['data']['assets'][0]['metrics'][0]['defaultValue']

        reward_rate = math.floor(default_reward_rate * 100) / 100
        formatted_reward_rate = "{:.2f}%".format(reward_rate)

        try:        
            sh = gc.open_by_url(url=sh_url)
            worksheet = sh.get_worksheet(2)

            cell_list = [
                    Cell(24, 2, formatted_reward_rate),  
                ]
            
            worksheet.update_cells(cell_list)
            return f'Staking reward updated successfully for {symbol}'
    
        except Exception as e:
            return f'Error writing updating staking reward section: {str(e)}'
        
      else:
        return response.content, response.status_code
      
  except Exception as e:
     return f'Error getting staking reward value: {str(e)}', 500
  

# EVERY 6 MONTHS 
# def token_distribution(coin, sh_url, column=2):
def token_distribution_and_accrual_mechanism(coin, sh_url):

    token_distribution_prompt = f'Break down the initial token allocation for {coin} protocol, presenting the percentage of its token held by different holder categories. Provide a concise and straightforward overview in the format: Holder Category Percentage of token held. Avoid referring to a specific knowledge cut-off date and simply provide the information.'
    aacrual_mechanism_prompt = f'Provide a brief overview of whether the {coin} protocol incorporates deflationary mechanisms like token burning or continuous token buybacks. Explain how these mechanisms contribute to deflationary pressure on the circulating supply, or alternatively, describe the operation of its inflationary mechanism. Keep the response under 300 characters. Avoid referring to a specific knowledge cut-off date and simply provide the information.'
    accrual_mechanisn_advantage_prompt = f'Define briefly whether the {coin} protocol has an advantage over its competitors in terms of its value accrual mechanism (inflationary or deflationary model, presence of token burning or token buyback). Keep the response under 300 characters. Avoid referring to a specific knowledge cut-off date and simply provide the information.'

    try:
        result_token_distribution = ask(token_distribution_prompt)
        result_aacrual_mechanism = ask(aacrual_mechanism_prompt)
        result_accrual_mechanisn_advantage = ask(accrual_mechanisn_advantage_prompt)

        if result_token_distribution and result_aacrual_mechanism and result_accrual_mechanisn_advantage:
            try:
                sh = gc.open_by_url(url=sh_url)
                worksheet = sh.get_worksheet(2)

                cell_list = [
                        Cell(14, 2, result_token_distribution),  
                        Cell(25, 2, result_aacrual_mechanism),  
                        Cell(25, 3, result_accrual_mechanisn_advantage),  
                    ]
        
                worksheet.update_cells(cell_list)
                return f'Token distribution updated successfully for {coin}'
            
            except Exception as e:
                return f'Error writing {coin} token distribution to the spreadsheet: {str(e)}'
    except Exception as e:
        return f'Error getting token distribution for {coin}'
    
# print(token_distribution('solana'))