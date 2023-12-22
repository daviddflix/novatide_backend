import gspread


gc = gspread.service_account(filename='app\\services\\service_account.json')

spreadsheet = gc.open_by_url('https://docs.google.com/spreadsheets/d/1pTKOrFj2x-L5KMO_AWhzMlw_axyHd3kFLKZKb9ZKaM8/edit#gid=1325184721')

worksheet = spreadsheet.get_worksheet(0) 

# Define data to be written
data_to_write = [
    ["Name", "Age", "Occupation"],
    ["John Doe", 25, "Engineer"],
    ["Jane Smith", 30, "Teacher"],
    # Add more rows as needed
]

# Write data to the worksheet
res = worksheet.update('A2:B4', [[42], [43]])

print("Data written successfully.")