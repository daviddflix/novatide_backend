import os
from openai import OpenAI
from dotenv import load_dotenv
from openai import APIError, RateLimitError, APIConnectionError

load_dotenv()
OPENAI_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI(
    api_key=OPENAI_KEY,
)

def ask_chatgpt(prompt, model="gpt-4-1106-preview"):

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[ 
            {"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=1024,
        )
        summary = response.choices[0].message.content
        return {'response': summary, 'success': True}

    except APIConnectionError as e:
        print(f"OpenAI API failed to establish a connection: {e}")
        return {'response': f"OpenAI API failed to establish a connection: {e}", 'success': False}
    except RateLimitError as e:
        print(f"OpenAI API request exceeded rate limit: {e}")
        return {'response': f"OpenAI API request exceeded rate limit: {e}", 'success': False}
    except APIError as e:
        print(f"OpenAI API returned an API Error: {e}")
        return {'response': f"OpenAI API returned an API Error: {e}", 'success': False}
    

