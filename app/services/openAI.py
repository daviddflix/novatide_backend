import os
from openai import OpenAI
from dotenv import load_dotenv
from openai import APIError, RateLimitError, APIConnectionError

load_dotenv()

OPENAI_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI(
    api_key=OPENAI_KEY,
)

def ask(prompt, model="gpt-4-1106-preview"):

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[ 
            {"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=1024,
        )
        summary = response.choices[0].message.content
        return summary

    except APIConnectionError as e:
        return f"OpenAI API failed to establish a connection : {e}"
    except RateLimitError as e:
        return f"OpenAI API request exceeded rate limit: {e}"
    except APIError as e:
        return f"OpenAI API returned an API Error: {e}"
    

