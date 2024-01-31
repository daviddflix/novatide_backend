# from gspread_formatting import CellFormat, Color, TextFormat
# from gspread_formatting import *
# import gspread
# import re
# import os
# from dotenv import load_dotenv

# # Load environment variables from the .env file
# load_dotenv()
# import requests
# from itertools import zip_longest

# gc = gspread.service_account(filename='app\\services\\service_account.json')

# # # For General
# # fmt_general = CellFormat(
# #     textFormat=TextFormat(bold=True),
# #     horizontalAlignment='CENTER',
# #     verticalAlignment='MIDDLE',
# #     wrapStrategy='WRAP',
# #     backgroundColor=Color(1, 0.8, 0.9)
# #     )

# # def change_color():

# #     sh = gc.open_by_url(url='https://docs.google.com/spreadsheets/d/19OQgMt_R7fTZwi4RIEqHNqoka9WhyLldj1Vz4vCDhEg/edit#gid=821358093')
# #     worksheet = sh.get_worksheet(0)
# #     format_cell_range(worksheet, 'B3:B3', fmt_general)

# # # change_color()

# # # # import re
# # # # import requests

# # # # def is_valid_url(url):
# # # #     try:
# # # #         response = requests.head(url, allow_redirects=True)
# # # #         return response.status_code == 200
# # # #     except requests.RequestException:
# # # #         return False

# # # # def extract_and_validate_urls(text):
# # # #     # Regular expression to find URLs in the given text
# # # #     url_pattern = re.compile(r'https?://\S+|<https?://\S+>|\[https?://\S+\]\(https?://\S+\)')

# # # #     # Extract URLs from the text
# # # #     urls = url_pattern.findall(text)

# # # #     # Validate and filter valid URLs
# # # #     valid_urls = [url.strip('<>[]()') for url in urls if is_valid_url(url.strip('<>[]()'))]

# # # #     # Return the result as a joined string
# # # #     result = ', '.join(valid_urls) if valid_urls else 'N/A'
# # # #     return result

# # # # # Example usage
# # # # case_1 = 'Sure, here is the link to the Fluence Network website: <https://fluence.network/>'
# # # # case_2 = 'Sure, here is the link to the bluejay-finance website: [https://www.bluejay-finance.com](https://www.bluejay-finance.com/)'
# # # # case_3 = "Sure! Here is the link to the koii-network Crypto Protocol website: <https://koii.network/>"
# # # # case_4 = 'Sure, here is the link to the Fluence Network website: https://fluence.network/'
# # # # case_5 = 'Sure, here is the link to the Fluence Network website: N/A'

# # # # print(extract_and_validate_urls(case_1))
# # # # print(extract_and_validate_urls(case_2))
# # # # print(extract_and_validate_urls(case_3))
# # # # print(extract_and_validate_urls(case_4))
# # # # print(extract_and_validate_urls(case_5))

# BASE_URL = 'https://pro-api.coingecko.com/api/v3'
# COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")

# headers = {
#             "Content-Type": "application/json",
#             "x-cg-pro-api-key": COINGECKO_API_KEY,
#         }


# def remove_symbol(input_string, symbol):
#     pattern = re.compile(re.escape(symbol))
#     result = pattern.sub(' ', input_string)
#     return result.casefold()

# # Returns a list of Dicts with all the available coins in Coingecko
# def get_list_of_coins():

#     try:
#         coingecko_response = requests.get(f'{BASE_URL}/coins/list', headers=headers)

#         if coingecko_response.status_code == 200:
#             return coingecko_response.json(), coingecko_response.status_code
#         else:
#             return coingecko_response.content, coingecko_response.status_code
#     except Exception as e:
#         print(f"Error: {str(e)}")
#         return None, None
            
# def get_spreadsheet_coinsV2(sh_url):
#     try:
#         sh = gc.open_by_url(url=sh_url)
#         worksheet = sh.get_worksheet(0)

#         coins_list = worksheet.col_values(1)
#         coins_symbols = worksheet.col_values(2)
       
#         if coins_list and coins_symbols:
#             list_of_coins, status = get_list_of_coins()
#             if status == 200:
#                 coins_dict = zip_longest(coins_list[1:], coins_symbols[1:], fillvalue='NA')

#                 result_dict_coins = []
#                 for coin_name, coin_symbol in coins_dict:

#                     coin_id = coin_name.casefold().strip()
#                     new_coin_id = remove_symbol(coin_id, '-')
#                     token_symbol = coin_symbol.casefold().strip()
                   
#                     if coin_symbol == '':
#                         coin_symbol = 'NA'

#                     for coin in list_of_coins:
#                         if new_coin_id == coin['name'].casefold() and token_symbol == coin['symbol']:
#                             print(f'{new_coin_id}  was replaced by {coin['id']}')
#                             new_coin_id = coin['id']
#                             break
#                         elif new_coin_id == coin['id']:
#                             break
                       
#                     result_dict_coins.append({'coin_id': new_coin_id, 'coin_symbol': coin_symbol})

#                 print(result_dict_coins)
#                 print(len())
#                 return result_dict_coins, 200
#             else:
#                 return 'Error while getting coins from Coingecko', 404
#         else:
#             return 'No coins were found in the spreadsheet', 404

#     except gspread.exceptions.APIError as e:
#         return f'Error accessing Google Sheets API - {str(e)}', 500

#     except Exception as e:
#         return f'Error getting coins - {str(e)}', 500

# # # # print(get_spreadsheet_coinsV2('https://docs.google.com/spreadsheets/d/19OQgMt_R7fTZwi4RIEqHNqoka9WhyLldj1Vz4vCDhEg/edit#gid=821358093'))
# get_spreadsheet_coinsV2('https://docs.google.com/spreadsheets/d/1c8MRF-JwjuvTX-Hd5dJNXuyQGizv2NdYhQHsHoMAp4g/edit#gid=821358093')



# market_data = 0


# fully_diluted_valuation = 'N/A' if market_data is None else market_data
# print('fully_diluted_valuation: ', fully_diluted_valuation)   



