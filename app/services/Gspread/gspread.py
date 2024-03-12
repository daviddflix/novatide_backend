import gspread
from pathlib import Path

ROOT_DIRECTORY = Path(__file__).parent.resolve()
print('ROOT_DIRECTORY: ', ROOT_DIRECTORY)

gc = gspread.service_account(filename=r'C:\Users\David\Documents\AI Alpha\FA Development\app\services\service_account.json')