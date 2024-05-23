import os
import requests
from dotenv import load_dotenv 


load_dotenv()
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

def perplexity_api_request(model, content, prompt):
    
    url = "https://api.perplexity.ai/chat/completions"
    prompt = prompt if prompt else "Be precise and concise"

    print('model',model)
    print('content',content)
    print('prompt',prompt)
    print('PERPLEXITY_API_KEY',PERPLEXITY_API_KEY)


    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": content
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
        print('res: ', response.status_code)
       
        response.raise_for_status()  

        choices = response.json().get('choices', [])
        if choices:
            assistant_message = choices[0].get('message', {})
            answer_content = assistant_message.get('content', None)
            
            if answer_content:
                return {'response': answer_content, 'success': True}
            else:
                return {'response': f"No answer found for this prompt: {prompt}. Error: {assistant_message}", 'success': False}
        else:
            return {'response': f"No choices found for this prompt: {prompt}, Error: {choices}", 'success': False}
    
    except requests.exceptions.RequestException as err:
        return {'response': f"Error during API request: {err}", 'success': False}


# Example usage
# formatted_token_name = 'ethereum'
# coin_analysis_prompt = f"Write a short paragraph (maximum 400 characters) explaining the {formatted_token_name} protocol, the problem it is trying to address and its main use cases."

# print(perplexity_api_request(model="codellama-70b-instruct",
#                        prompt=None,
#                        content=coin_analysis_prompt
#                        ))


