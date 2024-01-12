import re
import os
import gspread
import requests
from gspread.cell import Cell
from dotenv import load_dotenv
from app.services.openAI import ask
from app.services.perplexity import perplexity_api_request

# Load environment variables from the .env file
load_dotenv()

BASE_URL = 'https://pro-api.coingecko.com/api/v3'
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")
gc = gspread.service_account(filename='app\\services\\service_account.json')

def is_valid_https(link):
    try:
        response = requests.head(link)
        if response.status_code == 200:
            return True
        else:
            return False
    
    except requests.RequestException as e:
        return False

def extract_na_or_https(sentence):

    words = sentence.split()

    # These following two lines extracts the https link in sentence
    url_pattern = re.compile(r'https:\/\/[^\s]+')
    matches = url_pattern.findall(sentence)

     # These following two lines extracts the https link in sentence when the link is between <>
    https_matches = [re.match(r'<(https?://\S+)>', word) for word in words if re.match(r'<https?://\S+>', word)]
    https_links = [match.group(1) for match in https_matches] if https_matches else []

    na_present = 'N/A' in words

    if na_present:
        return 'N/A'
    if https_links:
        valid_https_links_ = [link for link in https_links if is_valid_https(link)]
        if valid_https_links_:
            return ' '.join(valid_https_links_)
        return 'N/A'
    if matches: 
        valid_https_links = [link for link in matches if is_valid_https(link)]
        if valid_https_links:
            return ' '.join(valid_https_links)
        return 'N/A'
    else:
        return 'N/A'

def round_up_and_format(number):
    # Round up the number to the nearest whole number
    rounded_number = round(number)

    # Determine the magnitude of the number (e.g., K, M, B)
    suffixes = ["", "K", "M", "B", "T"]
    magnitude = 0
    while abs(rounded_number) >= 1000 and magnitude < len(suffixes) - 1:
        rounded_number /= 1000.0
        magnitude += 1

    # Format the number with the appropriate suffix
    formatted_number = f"{rounded_number:.2f} {suffixes[magnitude]}"

    return formatted_number


# GETS THE DATA ONLY ONCE - CHAINS, CATEGORY, CONTRACT, COIN_LINK, WHITEPAPER, PROJECT SUMMARY
def get_once(coins, sh_url):

    headers = {
            "Content-Type": "application/json",
            "x-cg-pro-api-key": COINGECKO_API_KEY,
        }
    
    sh = gc.open_by_url(url=sh_url)
    worksheet = sh.get_worksheet(0)
        
    try:
        for coin_index, coin_name in enumerate(coins[2:]):
            coin_index = coin_index+3

            formatted_coin = str(coin_name).casefold().strip()
            response = requests.get(f'{BASE_URL}/coins/{formatted_coin}', headers=headers)
            
            whitepaper_prompt = f"Provide the direct link to the {formatted_coin} Crypto Protocol whitepaper. I'm interested in learning more. Please provide the link in a direct way, no additional words or information are needed. Do not present it, just provide the link. If there is no whitepaper available, simply respond with 'N/A'."
            website_prompt = f"Provide the link to the {formatted_coin}  Crypto Protocol website. I'm interested in learning more. Please provide the link in a direct way, no additional words or information are needed."
            chains_prompt = f'Simply state the blockchain on which  {formatted_coin} protocol is built. Please respond with the name of the chain, e.g. "Ethereum", no additional information is required, please avoid adding "The protocol is built on..." just state the name of the blockchain. Respond "Proprietary Layer 1" if it is built on its own blockchain. If the information is not available, simply answer "N/A".'
            category_prompt = f'Identify the primary category or sector of the following cryptocurrency protocol:  {formatted_coin}. Provide the main category or sector in which this protocol primarily operates. No additional information is required, please avoid adding extra information, just mention the category. If the information is not available, simply answer "N/A".'
            intro_prompt = f'Write a short paragraph (maximum 400 characters) explaining the {formatted_coin} protocol, the problem it is trying to address and its main use cases.'

            if response.status_code != 200:
                print(f'{formatted_coin} not found on coingecko, looking for data on perplexity...')
                
                whitepaper_response = perplexity_api_request(whitepaper_prompt)
                whitepaper_response = 'N/A' if whitepaper_response is None else extract_na_or_https(whitepaper_response)

                website_response = perplexity_api_request(website_prompt)
                website_response = 'N/A' if website_response is None else extract_na_or_https(website_response)

                chains_response = perplexity_api_request(chains_prompt)
                chains_response = 'N/A' if chains_response is None else extract_na_or_https(chains_response)

                category_response = perplexity_api_request(category_prompt)
                category_response = 'N/A' if category_response is None else extract_na_or_https(category_response)

                intro_response = perplexity_api_request(intro_prompt)

                if not whitepaper_response or not website_response or not chains_response or not category_response or not intro_response:
                    continue

                cell_list = [
                    Cell(coin_index, 3, website_response),  
                    Cell(coin_index, 5, intro_response),  
                    Cell(coin_index, 8, chains_response),  
                    Cell(coin_index, 9, category_response),  
                    Cell(coin_index, 7, whitepaper_response),  
                ]
            
                worksheet.update_cells(cell_list)
                continue

            
            # WHEN THE COIN IS NOT FOUND, IT FOLLOWS THIS WAY

            # project_summary = 'The centrifuge protocol aims'
            project_summary = ask(intro_prompt)
            project_summary = 'N/A' if project_summary.startswith('OpenAI API') else project_summary

            whitepaper = perplexity_api_request(whitepaper_prompt)
            whitepaper = extract_na_or_https(whitepaper)

            response_json = response.json()

            # Gets the homepage_link, N/A if not found
            homepage_link = response_json["links"]["homepage"][0]
            homepage_link = homepage_link if homepage_link else 'N/A'

            # Gets the categories, N/A if not found
            categories = [category for category in response_json["categories"] if 'ecosystem' not in category.lower()]
            categories = ", ".join(categories) if categories else extract_na_or_https(perplexity_api_request(category_prompt))

            
            chains = [category for category in response_json["categories"] if 'ecosystem' in category.lower()]
            chains = ", ".join(chains) if chains else 'N/A'
            
            # Gets the contract, N/A if not found
            platforms = response_json.get("detail_platforms", None)
            if platforms and any(details.get('contract_address') or details.get('decimal_place') is not None for details in platforms.values()):
                contract_addresses = [
                    f"{platform}: {details.get('contract_address', 'N/A')}"
                    for platform, details in platforms.items()
                    if details.get('contract_address') or details.get('decimal_place') is not None
                ]
                contract_addresses = "\n".join(contract_addresses)
            else:
                contract_addresses = 'N/A'

            
            coingecko_link = f'https://www.coingecko.com/en/coins/{formatted_coin}'


            cell_list = [
                    Cell(coin_index, 3, homepage_link),  
                    Cell(coin_index, 5, project_summary),  
                    Cell(coin_index, 8, chains),  
                    Cell(coin_index, 9, categories),  
                    Cell(coin_index, 18, contract_addresses),  
                    Cell(coin_index, 21, coingecko_link),  
                    Cell(coin_index, 7, whitepaper),  
                ]
            
            worksheet.update_cells(cell_list)

        return 'ok', 200 
        
    except Exception as e:
        print(f'Error updating data once {str(e)}')
    

# GETS THE DATA ONCE A DAY - ATH / % VARIATION, MARKET CAP, CURRENT PRICE, PRICE CHANGE 1Y, YEARLY PRICE  
def get_once_a_day(coins, sh_url):

    headers = {
            "Content-Type": "application/json",
            "x-cg-pro-api-key": COINGECKO_API_KEY,
        }
    
    sh = gc.open_by_url(url=sh_url)
    worksheet = sh.get_worksheet(0)

    try: 
        for coin_index, coin_name in enumerate(coins[2:]): 
            coin_index = coin_index+3
          
            availability_price_one_year  = worksheet.cell(coin_index, 12).value

            if not availability_price_one_year:
                cell_list = [
                    Cell(coin_index, 13, 'Availability from one year ago price not found or is invalid')
                    ]
                worksheet.update_cells(cell_list)
                 
            is_yearly_price_available = True if availability_price_one_year.strip() == '✔️' else False

            formatted_coin = str(coin_name).casefold().strip()
            response = requests.get(f'{BASE_URL}/coins/{formatted_coin}', headers=headers)
            
            if response.status_code !=200:
                continue
            
            response_json = response.json()
            
            market_data = response_json.get('market_data')

            ath = 'N/A' if market_data['ath'] is None else market_data['ath']['usd']
            ath_percentage = 'N/A' if market_data['ath_change_percentage'] is None else market_data['ath_change_percentage']['usd']
            ath_formatted = f'${ath}, {ath_percentage}%'

            market_cap = 'N/A' if market_data['market_cap'] is None else market_data['market_cap']['usd']
            formatted_market_Cap = round_up_and_format(market_cap)

            current_price = 'N/A' if market_data['current_price'] is None else f"${market_data['current_price']['usd']}"
            price_change_percentage_1y = 'N/A' if market_data['price_change_percentage_1y'] is None else f"{market_data['price_change_percentage_1y']:,.4f}%"
            
            yearly_price = 'N/A'
            if is_yearly_price_available and current_price != 'N/A' and market_cap != 'N/A':
                yearly_price = market_data['current_price']['usd'] / (1 + market_data['price_change_percentage_1y'] / 100)
                yearly_price = f"{yearly_price:,.4f}"

            cell_list = [
                    Cell(coin_index, 10, formatted_market_Cap),  
                    Cell(coin_index, 11, current_price),  
                    Cell(coin_index, 13, yearly_price),  
                    Cell(coin_index, 14, price_change_percentage_1y),  
                    Cell(coin_index, 22, ath_formatted),  
                ]
           
            worksheet.update_cells(cell_list)
    
    except Exception as e:
        print(f'Error in get_once_a_day {str(e)}')
    


def get_once_a_month(coins, sh_url):

    headers = {
            "Content-Type": "application/json",
            "x-cg-pro-api-key": COINGECKO_API_KEY,
        }
    
    sh = gc.open_by_url(url=sh_url)
    worksheet = sh.get_worksheet(0)

    try: 
        for coin_index, coin_name in enumerate(coins[2:]):
            
            
            coin_index = coin_index+3
            formatted_coin = str(coin_name).casefold().strip()
        
            response = requests.get(f'{BASE_URL}/coins/{formatted_coin}', headers=headers)

            if response.status_code !=200:
                continue

            response_json = response.json()
            market_data = response_json.get('market_data')
          
            max_supply_str = 'Infinite' if market_data['max_supply'] is None else f"${market_data['max_supply']:,.2f}"

            supply_model = 'Inflationary' if market_data['max_supply'] is None else 'Deflationary'
     
            fully_diluted_valuation = 'N/A' if market_data['fully_diluted_valuation'] is None else market_data['fully_diluted_valuation']['usd']          
            formatted_fully_diluted = round_up_and_format(fully_diluted_valuation)

            circulating_supply_str = 'N/A' if market_data['circulating_supply'] is None else market_data['circulating_supply']
            formatted_circulating_supply = round_up_and_format(circulating_supply_str)
            
            circulating_supply_percentage = '100%' if max_supply_str == 'Infinite' else (int(market_data['circulating_supply']) / int(market_data['max_supply'])) * 100
            circulating_supply_percentage = f"{circulating_supply_percentage:,.2f}%" if circulating_supply_percentage != '100%' else '100%'

        
            cell_list = [
                    Cell(coin_index, 15, formatted_fully_diluted),  
                    Cell(coin_index, 16, circulating_supply_percentage),  
                    Cell(coin_index, 17, supply_model),  
                    Cell(coin_index, 19, formatted_circulating_supply),  
                    Cell(coin_index, 20, max_supply_str),  
                ]
        
            worksheet.update_cells(cell_list)  

    
    except Exception as e:
        print(f'Error in get_once_a_month: {str(e)}')

    



    

