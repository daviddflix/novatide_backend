import os
from dotenv import load_dotenv
from dextools_python import DextoolsAPIV2

# Load environment variables from the .env file
load_dotenv()

DEXTOOL_API_KEY = os.getenv("DEXTOOL_API_KEY")
dextools = DextoolsAPIV2(DEXTOOL_API_KEY, plan="standard")

# Gets token liquidity
def get_token_liquidity(token_id, address):
    try:
        response = dextools.get_pool_liquidity(token_id, address)
        status = response['statusCode']

        if status == 200:
            return {'message': response['data'], 'success': True}
       
        return {'message': response['message'], 'success': False}
    except Exception as e:
        return {'message': str(e), 'success': False}
    

# Gets the data for a single token: name, website and ID.
def get_token_info(token_id):
    try:
        response = dextools.get_blockchain(token_id)
        status = response['statusCode']

        if status == 200:
            return {'message': response['data'], 'success': True}
       
        return {'message': response['message'], 'success': False}
    except Exception as e:
        return {'message': str(e), 'success': False}


# Gets all data for all the available token by Page
def get_all_tokens_info():
    try:
        all_data = []
        page = 0

        while True:
            response = dextools.get_blockchains(sort="name", page=page)
            status = response.get('statusCode')

            if status == 200:
                page_data = response['data']['results']
                all_data.extend(page_data)

                # Check if there are more pages
                if not page_data:
                    break

                page += 1
            else:
                return {'message': response.get('message', 'Unknown error'), 'success': False}
        
        # Write all_data to a text file
        with open('all_data.txt', 'w') as file:
            for item in all_data:
                file.write(str(item) + '\n')
        
        return {'data': all_data, 'success': True}

    except Exception as e:
        return {'message': str(e), 'success': False}
    

# Gets all the dexes of a token
def get_all_dexes_of_token(token_id):
    try:
        all_data = []
        page = 0

        while True:
            response = dextools.get_dexes(sort="name", page=page, chain=token_id)
            status = response.get('statusCode')

            if status == 200:
                page_data = response['data']['results']
                all_data.extend(page_data)

                # Check if there are more pages
                if not page_data:
                    break

                page += 1
            else:
                return {'message': response.get('message', 'Unknown error'), 'success': False}
        
        # Write all_data to a text file
        with open('all_data.txt', 'w') as file:
            for item in all_data:
                file.write(str(item) + '\n')
        
        return {'data': all_data, 'success': True}

    except Exception as e:
        return {'message': str(e), 'success': False}


pool_price = dextools.get_pool_price("ether", "0x97be09f2523b39b835da9ea3857cfa1d3c660cbb")
print(pool_price)
# print(get_token_liquidity(token_id="ether", address="0xdb5247366afd7712e6dcaffa3e7077423a852f65"))
# blockchain = dextools.get_blockchain("ether")
# print(blockchain)
# blockchains = dextools.get_blockchains()
# print(blockchains)
# get_all_tokens_info()

