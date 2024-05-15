import os
import json
import time
import requests
from dotenv import load_dotenv


# Load environment variables from the .env file
load_dotenv()
DEXTOOL_API_KEY = os.getenv("DEXTOOL_API_KEY")
BASE_URL = 'https://public-api.dextools.io/standard/v2'


# get data of a blockchain if passed otherwise all
def get_blockchain_data(chain_name=None):
    try:
        all_results = []
        page = 0
        while True:
            url = f"{BASE_URL}/blockchain"
            params = {'sort': 'name', 'order': 'asc', 'page': page}
            headers = {'accept': 'application/json', 'x-api-key': DEXTOOL_API_KEY}
            response = requests.get(url, params=params, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                all_chains = data['data']['results']
              
                if chain_name:
                    for x in all_chains:
                        chain_id_of_current_blockchain = x.get('name')
                        if chain_id_of_current_blockchain and chain_id_of_current_blockchain.casefold() == chain_name.casefold():
                            all_results.append(x)
                else:
                    all_results.extend(all_chains)
                
                # If there are more pages, increment the page number and continue
                if page < data['data']['totalPages'] - 1:
                    page += 1
                else:
                    break
            else:
                return {'response': None, 'status': response.status_code, 'success': False}
        
        # # Save the data to a JSON file
        # with open('blockchain_data.json', 'w') as json_file:
        #     json.dump(all_results, json_file, indent=4)
        #     print('--Blockchain data saved--')
        
        
        return {'response': all_results, 'status': 200, 'success': True}
    except Exception as e:
        return {'response': None, 'status': 500, 'success': False, 'error': str(e)}


# Example usage
# print('BLOCKCHAINS:', get_blockchain_data(chain_name='ethereum'))



# ------------------------------------------------------


def get_token_data(chain_id='ether', sort='creationTime', order='asc', from_date=None, to_date=None):
    try:
        all_results = []
        page = 0
        if from_date is None:
            from_date = "2022-01-01T00:00:00.000Z"  # Default from date
            
        if to_date is None:
            to_date = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())  # Current datetime
        
        while True:
            url = f"{BASE_URL}/token/{chain_id}"
            params = {'sort': sort, 'order': order, 'from': from_date, 'to': to_date, 'page': page}
            headers = {'accept': 'application/json', 'x-api-key': DEXTOOL_API_KEY}
            response = requests.get(url, params=params, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print('data: ', data)
                all_tokens = data['data']['tokens']
                all_results.extend(all_tokens)
                
                # If there are more pages, increment the page number and continue
                if page < data['data']['totalPages'] - 1:
                    page += 1
                else:
                    break
            else:
                return {'response': None, 'status': response.status_code, 'success': False}
       
        # Save the data to a JSON file
        with open('token_data.json', 'w') as json_file:
            json.dump(all_results, json_file, indent=4)
            print('--Token data saved--')
        
        return {'response': all_results, 'status': 200, 'success': True}
    except Exception as e:
        return {'response': None, 'status': 500, 'success': False, 'error': str(e)}

# Example usage:
# print('TOKEN DATA:', get_token_data())


def get_token_score(chain_id, token_address):
    try:
        url = f"{BASE_URL}/token/{chain_id}/{token_address}/score"
        headers = {'accept': 'application/json', 'x-api-key': DEXTOOL_API_KEY}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return {'response': response.json(), 'status': 200, 'success': True}
        else:
            return {'response': None, 'status': response.status_code, 'success': False}
    except Exception as e:
        return {'response': None, 'status': 500, 'success': False, 'error': str(e)}

# Example usage:
# chain_id = "ether"
# token_address = "0xfb7b4564402e5500db5bb6d63ae671302777c75a"
# print('TOKEN SCORE:', get_token_score(chain_id, token_address))


def get_token_audit(chain_id, token_address):
    try:
        url = f"{BASE_URL}/token/{chain_id}/{token_address}/audit"
        headers = {'accept': 'application/json', 'x-api-key': DEXTOOL_API_KEY}
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return {'response': response.json(), 'status': 200, 'success': True}
        else:
            return {'response': None, 'status': response.status_code, 'success': False}
    except Exception as e:
        return {'response': None, 'status': 500, 'success': False, 'error': str(e)}

# Example usage:
# chain_id = "ether"
# token_address = "0xfb7b4564402e5500db5bb6d63ae671302777c75a"
# print('TOKEN AUDIT:', get_token_audit(chain_id, token_address))



def get_dextool_data(chain_name, address):
    try:
        if not chain_name or not address:
            return {'error': 'chain name and address are required', 'success': False}
        
        dextool_data = {}
        chain_data = get_blockchain_data(chain_name=chain_name)
        if chain_data['success']:
            chain_id = chain_data['response'][0]['id']
            token_score = get_token_score(chain_id=chain_id, token_address=address)
            
            # SCORE VALUES
            if token_score['success']:
                score_data = token_score['response']
                
                # Extracting the values
                total_score = score_data["data"]["dextScore"]["total"]
                upvotes = score_data["data"]["votes"]["upvotes"]
                downvotes = score_data["data"]["votes"]["downvotes"]

                # Calculating total votes
                total_votes = upvotes + downvotes

                # Calculating the upvote ratio
                upvote_ratio = upvotes / total_votes

                # Converting the ratio to a percentage
                percentage_score = upvote_ratio * 100

                # Calculating the final score
                final_score = (percentage_score / 100) * total_score

                # Rounding the score
                final_score_rounded = round(final_score)

                formatted_score = f"{final_score_rounded}/{total_score}"
                dextool_data['score'] = formatted_score

            # TAX, MINTABLE, VALATILITY, BLACKLISTED...
            token_audits = get_token_audit(chain_id=chain_id, token_address=address)
            if token_audits['success']:
                audits_data = token_audits['response']
                
                dextool_data['isHoneypot'] = audits_data['data']['isHoneypot']
                dextool_data['isProxy'] = audits_data['data']['isProxy']
                dextool_data['isBlacklisted'] = audits_data['data']['isBlacklisted']
                dextool_data['sellTax'] = audits_data['data']['sellTax']['max']
                dextool_data['buyTax'] = audits_data['data']['buyTax']['max']
                dextool_data['isPotentiallyScam'] = audits_data['data']['isPotentiallyScam']
                dextool_data['isContractRenounced'] = audits_data['data']['isContractRenounced']


        return {'data': dextool_data, 'success': True}
    except Exception as e:
        return {'error': str(e), 'success': False}


# print(get_dextool_data(chain_name='ethereum', address='0xfb7b4564402e5500db5bb6d63ae671302777c75a'))
















# def get_dex_data():
#     url = "https://public-api.dextools.io/standard/v2/dex/polygon"
#     headers = {
#         "accept": "application/json",
#         "x-api-key": "nqh7hql3Op3xnTIH7fvkY7i58dOJ8mxr1tUeHFTh"
#     }

#     try:
#         response = requests.get(url, headers=headers, params={"sort": "name", "order": "asc"})
#         response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes

#         # Check if the response contains JSON data
#         if response.headers.get("content-type") == "application/json":
#             data = response.json()
#             return {'response': data, 'status': response.status_code, 'success': True, 'error': None}
#         else:
#             return {'response': None, 'status': response.status_code, 'success': False, 'error': 'Response is not JSON'}

#     except requests.exceptions.RequestException as e:
#         return {'response': None, 'status': 500, 'success': False, 'error': str(e)}
#     except ValueError as e:
#         return {'response': None, 'status': 500, 'success': False, 'error': 'Failed to decode JSON: ' + str(e)}
#     except Exception as e:
#         return {'response': None, 'status': 500, 'success': False, 'error': 'An unexpected error occurred: ' + str(e)}

# print(get_dex_data())