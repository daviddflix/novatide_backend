import os
import requests
from dotenv import load_dotenv 

load_dotenv()

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

def perplexity_api_request(question, model="codellama-34b-instruct"):
    url = "https://api.perplexity.ai/chat/completions"

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "Be precise and concise."
            },
            {
                "role": "user",
                "content": question
            }
        ]
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  

        choices = response.json().get('choices', [])
        if choices:
            assistant_message = choices[0].get('message', {})
            answer_content = assistant_message.get('content', None)
            
            if answer_content:
                return answer_content
            else:
                print("No answer content found in the API response.")
                return None
        else:
            print("No choices found in the API response.")
            return None
    
    except requests.exceptions.RequestException as err:
        print(f"Error during API request: {err}")
        return None

# Example usage:
# question_to_ask = f'Simply state the blockchain on which Centrifuge protocol is built. Please respond with the name of the chain, e.g. "Ethereum", no additional information is required, please avoid adding "The protocol is built on..." just state the name of the blockchain. Respond "Proprietary Layer 1" if it is built on its own blockchain. If the information is not available, simply answer "N/A".'

# text_answer = perplexity_api_request(question_to_ask)

# if text_answer:
#     print("Text Answer:", text_answer)
# else:
#     print("Failed to get a valid text answer from the API response.")
