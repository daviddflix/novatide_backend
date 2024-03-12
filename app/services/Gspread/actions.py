import gspread
from itertools import zip_longest 
from app.services.Gspread.gspread import gc
from app.services.CoinGecko.actions import get_list_of_coins

# Gets all the coins in the spreadsheet in a single list
def get_spreadsheet_coinsV2(sh_url, sheet_index=0):
    try:
        sh = gc.open_by_url(url=sh_url)
        worksheet = sh.get_worksheet(sheet_index)

        coins_list = worksheet.col_values(1)
        coins_symbols = worksheet.col_values(2)
        print('length coins list:', len(coins_list))
        print('coins list:', coins_list)
        print('\nlength coins symbols:', len(coins_symbols))
        print('coins symbols:', coins_symbols)

        if coins_list and coins_symbols:

            list_of_coins, status = get_list_of_coins()
          
        #     if status == 200:
        #         coins_dict = zip_longest(coins_list[1:], coins_symbols[1:], fillvalue='NA')

        #         result_dict_coins = []
        #         for coin_name, coin_symbol in coins_dict:
        #             if coin_symbol == '':
        #                 coin_symbol = 'NA'

        #             coin_id = coin_name

        #             for coin in list_of_coins:
        #                 if coin_id.casefold().strip() == coin['name'].casefold().strip():
        #                     print('coin_id: ', coin_id)
        #                     print('Coingecko name: ', coin['name'])
        #                     coin_id = coin['id']
        #                     break
        #                 elif coin_id.casefold().strip() == coin['id'].casefold().strip():
        #                     print('coin_id: ', coin_id)
        #                     print('Coingecko id: ', coin['id'])
        #                     break
                       
        #             result_dict_coins.append({'coin_id': coin_id.casefold().strip(), 'coin_symbol': coin_symbol.casefold().strip()})

        #         return result_dict_coins, 200
        #     else:
        #         return 'Error while getting coins from Coingecko', 404
        # else:
        #     return 'No coins were found in the spreadsheet', 404

    except gspread.exceptions.APIError as e:
        return f'Error accessing Google Sheets API - {str(e)}', 500

    except Exception as e:
        return f'Error getting coins - {str(e)}', 500
    


# # Updates a single cell
# def update_cell(cell, worksheet, message="Coin not found. Looking for more data..."):
#     try:
#         cell_list = [
#             Cell(cell, 3, message)
#             ]
            
#         worksheet.update_cells(cell_list)
#         return f'Cell {cell} updated', 200
    
#     except gspread.exceptions.APIError as e:
#         return 'Error accessing Google Sheets API', 500

#     except Exception as e:
#         return 'Error updating cell', 500