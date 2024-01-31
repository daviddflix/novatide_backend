import re
import os
import gspread
import time
import requests
from gspread.cell import Cell
from dotenv import load_dotenv
from app.services.openAI import ask
from app.services.perplexity import perplexity_api_request
from gspread_formatting import CellFormat, Color, TextFormat
from gspread_formatting import *
from app.services.coinmarketcap import get_crypto_metadata



# Load environment variables from the .env file
load_dotenv()

BASE_URL = 'https://pro-api.coingecko.com/api/v3'
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")
gc = gspread.service_account(filename='app\\services\\service_account.json')

# For RED
fmt_red = CellFormat(
    textFormat=TextFormat(bold=True, foregroundColor=Color(1, 0, 0)),
    horizontalAlignment='CENTER',
    verticalAlignment='MIDDLE',
    wrapStrategy='WRAP'
    )

# For GREEN
fmt_green = CellFormat(
    textFormat=TextFormat(bold=True, foregroundColor=Color(0, 0.8, 0)),
    horizontalAlignment='CENTER',
    verticalAlignment='MIDDLE',
    wrapStrategy='WRAP'
    )

# For General
fmt_general = CellFormat(
    textFormat=TextFormat(bold=True),
    horizontalAlignment='CENTER',
    verticalAlignment='MIDDLE',
    wrapStrategy='WRAP'
    )

# For Coin not found
fmt_coin_not_found = CellFormat(
    textFormat=TextFormat(bold=True),
    horizontalAlignment='CENTER',
    verticalAlignment='MIDDLE',
    wrapStrategy='WRAP',
    backgroundColor=Color(1, 0.8, 0.9)
)




def is_valid_url(url):
    try:
        response = requests.head(url, allow_redirects=True)
        return response.status_code == 200
    except requests.RequestException:
        return False


def extract_and_validate_urls(text):
    # Regular expression to find URLs in the given text
    url_pattern = re.compile(r'https?://\S+|<https?://\S+>|\[https?://\S+\]\(https?://\S+\)')

    # Extract URLs from the text
    urls = url_pattern.findall(text)

    # Validate and filter valid URLs
    valid_urls = [url.strip('<>[]()') for url in urls if is_valid_url(url.strip('<>[]()'))]

    # Return the result as a joined string
    result = ', '.join(valid_urls) if valid_urls else 'N/A'
    return result


# Rounds up the number and adds a letter at the end indiciating its number.
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


# Checks if the price is potive, negative or zero.
def check_price(price):
    try:
        cleaned_price = price.rstrip('%')
        price_value = float(cleaned_price)

        if price_value > 0:
            return "Positive"
        elif price_value < 0:
            return "Negative"
        else:
            return "Zero"
    except ValueError:
        return "Invalid input: Not a valid number"


# GETS THE DATA ONLY ONCE - CHAINS, CATEGORY, CONTRACT, COIN_LINK, WHITEPAPER, PROJECT SUMMARY
def get_once(coins, sh_url):

    headers = {
            "Content-Type": "application/json",
            "x-cg-pro-api-key": COINGECKO_API_KEY,
        }

    
    sh = gc.open_by_url(url=sh_url)
    worksheet = sh.get_worksheet(0)

    set_row_height(worksheet, '2:200', 200)
    set_column_width(worksheet, 'E:E', 380)
        
    try:
        for coin_index, coin_name in enumerate(coins):
            
            coin_index = coin_index+2
            coin_id = coin_name['coin_id']
            coin_symbol = coin_name['coin_symbol']

            general_cells = f'C{coin_index}:V{coin_index}'
            format_cell_range(worksheet, general_cells, fmt_general)

            response = requests.get(f'{BASE_URL}/coins/{coin_id}', headers=headers)

            white_paper_coinmarket = 'N/A'
            if coin_symbol.casefold() != 'na' or coin_symbol.casefold() is None:
                whitepaper = get_crypto_metadata(coin_symbol)
                white_paper_coinmarket = 'N/A' if coin_symbol is None else ('N/A' if whitepaper is None else whitepaper)

            website_prompt = f"Provide the link to the {coin_id}  Crypto Protocol website. I'm interested in learning more. Please provide the link in a direct way, no additional words or information are needed."
            intro_prompt = f'Write a short paragraph (maximum 400 characters) explaining the {coin_id} protocol, the problem it is trying to address and its main use cases.'

            if response.status_code != 200:
                print(f'{coin_id} not found on coingecko, looking for data on perplexity...')   

                if white_paper_coinmarket == 'N/A':
                    empty_cells = f'G{coin_index}:V{coin_index}'
                    format_cell_range(worksheet, empty_cells, fmt_coin_not_found)
                else:
                    empty_cells = f'H{coin_index}:V{coin_index}'
                    format_cell_range(worksheet, empty_cells, fmt_coin_not_found)

                symbol_cell = f'B{coin_index}:B{coin_index}'
                format_cell_range(worksheet, symbol_cell, fmt_coin_not_found)
                
                website_response = perplexity_api_request(website_prompt)
                website_extracted_text = 'N/A' if website_response is None else extract_and_validate_urls(website_response)
               
                intro_response = perplexity_api_request(intro_prompt)
                intro_response = 'N/A' if intro_response is None else intro_response

                if not website_response or not intro_response:
                    continue

                cell_list = [
                    Cell(coin_index, 3, website_extracted_text),  
                    Cell(coin_index, 5, intro_response),  
                    Cell(coin_index, 8, 'N/A'),  
                    Cell(coin_index, 9, 'N/A'),  
                    Cell(coin_index, 10, 'N/A'),  
                    Cell(coin_index, 7, white_paper_coinmarket),  
                ]
            
                worksheet.update_cells(cell_list)
                time.sleep(40)
                continue
            else:
            
                # WHEN THE COIN IS NOT FOUND, IT FOLLOWS THIS WAY

                project_summary = ask(intro_prompt)
                project_summary = 'N/A' if project_summary.startswith('OpenAI API') else project_summary

                response_json = response.json()

                # Gets the homepage_link, N/A if not found
                homepage_link = response_json["links"]["homepage"][0]
                homepage_link = homepage_link if homepage_link else 'N/A'

                # Gets the categories, N/A if not found
                categories = [category for category in response_json["categories"] if 'ecosystem' not in category.lower()]
                categories = ", ".join(categories) if categories else 'N/A'

                
                chains = [category for category in response_json["categories"] if 'ecosystem' in category.lower()]
                chains = ", ".join(chains) if chains else 'N/A'
                
                # Gets the contract, N/A if not found
                platforms = response_json.get("detail_platforms", None)
                print('platforms: ', platforms)
                if platforms and any(details.get('contract_address') or details.get('decimal_place') is not None for details in platforms.values()):
                    contract_addresses = [
                        f"{platform}: {details.get('contract_address', 'N/A')}"
                        for platform, details in platforms.items()
                        if details.get('contract_address') or details.get('decimal_place') is not None
                    ]
                    contract_addresses = "\n".join(contract_addresses)
                else:
                    contract_addresses = 'N/A'
                
                print('contract_addresses: ', contract_addresses)

                
                coingecko_link = f'https://www.coingecko.com/en/coins/{coin_id}'
                print('coingecko_link: ', coingecko_link)


                cell_list = [
                        Cell(coin_index, 3, homepage_link),  
                        Cell(coin_index, 5, project_summary),  
                        Cell(coin_index, 8, chains),  
                        Cell(coin_index, 9, categories),  
                        Cell(coin_index, 18, contract_addresses),  
                        Cell(coin_index, 21, coingecko_link),  
                        Cell(coin_index, 7, white_paper_coinmarket),  
                    ]
                
                worksheet.update_cells(cell_list)
                time.sleep(40)

        return f'data for {sh_url} updated once', 200 
        
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
        for coin_index, coin_name in enumerate(coins): 
            coin_index = coin_index+2
            coin_id = coin_name['coin_id']
            
            formatted_coin = str(coin_id).casefold().strip()
            response = requests.get(f'{BASE_URL}/coins/{formatted_coin}', headers=headers)
                       
            if response.status_code !=200:
                print(f'{coin_id} not found...')
                continue
            else:

                availability_price_one_year  = worksheet.cell(coin_index, 12).value

                is_yearly_price_available = False
                if not availability_price_one_year:
                    cell_list = [
                        Cell(coin_index, 13, 'Availability from one year ago price not found or is invalid')
                        ]
                    worksheet.update_cells(cell_list)
                else:    
                    is_yearly_price_available = True if availability_price_one_year.strip() == '✔️' else False
                
                response_json = response.json()
                
                market_data = response_json.get('market_data')
                print(f'\n\nGet once a day data: {coin_id}')

                ath = 'N/A' if market_data['ath'] is None else market_data['ath']['usd']
                print('ath: ', ath)
                ath_percentage = 'N/A' if market_data['ath_change_percentage'] is None else market_data['ath_change_percentage']['usd']
                print('ath_percentage: ', ath_percentage)
                ath_formatted = f'${ath}, {ath_percentage}%'
                print('ath_formatted: ', ath_formatted)

                market_cap = 'N/A' if market_data['market_cap'] is None else market_data['market_cap']['usd']
                print('market_cap: ', market_cap)
                formatted_market_Cap = 'N/A...'
                if market_cap != 'N/A':
                    formatted_market_Cap =  round_up_and_format(market_cap)

                current_price = 'N/A' if market_data['current_price'] is None else f"${market_data['current_price']['usd']}"
                print('current_price: ', current_price)
              
                price_change_percentage_1y = 'N/A' if market_data['price_change_percentage_1y'] is None else f"{market_data['price_change_percentage_1y']:,.4f}%"
                print('price_change_percentage_1y: ', price_change_percentage_1y)
                if price_change_percentage_1y != 'N/A':
                    cells = f'N{coin_index}:N{coin_index}'
                    price = check_price(price_change_percentage_1y)
                    if price == 'Positive':
                        format_cell_range(worksheet, cells, fmt_green)
                    elif price == 'Negative':
                        format_cell_range(worksheet, cells, fmt_red)
                    else:
                        None

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
                time.sleep(40)

        return f'data for {sh_url} updated once a day', 200
    
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
        for coin_index, coin_name in enumerate(coins):
            
            coin_index = coin_index+2
            coin_id = coin_name['coin_id']
        
            response = requests.get(f'{BASE_URL}/coins/{coin_id}', headers=headers)

            if response.status_code !=200:
                print(f'{coin_id} not found...')
                continue
            else:
                response_json = response.json()
                market_data = response_json.get('market_data')
                print(f'\nGet once a month data: {coin_id}')
            
                max_supply_str = 'Infinite' if market_data['max_supply'] is None else f"${market_data['max_supply']:,.2f}"
                print('max_supply_str: ', max_supply_str)

                supply_model = 'Inflationary' if market_data['max_supply'] is None else 'Deflationary'
                print('supply_model: ', supply_model)
        
                fully_diluted_valuation = 'N/A' if not market_data['fully_diluted_valuation'] else market_data['fully_diluted_valuation']['usd']          
                print('fully_diluted_valuation: ', fully_diluted_valuation)
                formatted_fully_diluted = 'N/A' if fully_diluted_valuation == 'N/A' else round_up_and_format(fully_diluted_valuation)
                print('formatted_fully_diluted: ', formatted_fully_diluted)
                circulating_supply_str = 'N/A' if market_data['circulating_supply'] is None else market_data['circulating_supply']
                print('circulating_supply_str:', circulating_supply_str)
                formatted_circulating_supply = 'N/A' if circulating_supply_str == 'N/A' else round_up_and_format(circulating_supply_str)
                print('formatted_circulating_supply: ', formatted_circulating_supply)
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
                time.sleep(40) 

        return f'data for {sh_url} updated once a month', 200
    
    except Exception as e:
        print(f'Error in get_once_a_month: {str(e)}')

    



    

