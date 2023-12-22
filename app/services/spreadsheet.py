
import gspread
from gspread.cell import Cell

gc = gspread.service_account(filename='app\\services\\service_account.json')

def write_data_to_tokenomics_feature_section(sh_url, column, data):
    
    try:    

            total_supply = data[0]
            circulating_supply = data[1]
            circulating_supply_percentage = data[2]
            max_supply = data[3]
            supply_model = data[4]
            last_updated = data[5]

            sh = gc.open_by_url(url=sh_url)
            worksheet = sh.get_worksheet(2)
        
            cell_list = [
                Cell(3, column, total_supply),  
                Cell(4, column, circulating_supply), 
                Cell(5, column, circulating_supply_percentage),  
                Cell(6, column, max_supply),  
                Cell(7, column, supply_model),  
                Cell(8, column, last_updated),  
            ]

            response = worksheet.update_cells(cell_list)
            
            return 'Feature section updated successfully'
        
    except Exception as e:
        return f'Error writing data to the feature section: {str(e)}'


def write_data_to_tokenomics_mechanism_section(sh_url, data, column=2):
     
    try:
        staking_reward = data[0]
        
        sh = gc.open_by_url(url=sh_url)
        worksheet = sh.get_worksheet(2)

        #line 48 modified on 20/12 change to right cell
        cell_list = [
                Cell(18, column, staking_reward),  
            ]
        
        worksheet.update_cells(cell_list)
        return 'Mechanism section updated successfully'
    
    except Exception as e:
        return f'Error writing data to Mechanism section: {str(e)}'


def write_data_to_introduction_section(sh_url, data, column=2):
     
    try:
        market_cap = data[0]
        daily_trading_volumn = data[1]

        sh = gc.open_by_url(url=sh_url)
        worksheet = sh.get_worksheet(1)

        cell_list = [
                Cell(10, column, market_cap),  
                Cell(11, column, daily_trading_volumn),  
            ]
        
        worksheet.update_cells(cell_list)
        return 'Introduction section updated successfully'
    
    except Exception as e:
        return f'Error writing data to the Introduction section: {str(e)}'
