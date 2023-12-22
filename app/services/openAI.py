import os
from openai import OpenAI
from dotenv import load_dotenv
from openai import APIError, RateLimitError, APIConnectionError

load_dotenv()

OPENAI_KEY = os.getenv('OPENAI_API_KEY')

client = OpenAI(
    api_key=OPENAI_KEY,
)

def ask(prompt, model="gpt-4"):

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
        return f"Failed to connect to OpenAI API: {e}"
    except RateLimitError as e:
        return f"OpenAI API request exceeded rate limit: {e}"
    except APIError as e:
        return f"OpenAI API returned an API Error: {e}"
    

# print(ask(prompt="Write a short paragraph (maximum 400 characters) explaining the problem addressed by ethereum cryptocurrency project and evaluate its effectiveness in solving it, using formal language. Analyze its positioning in the market without using adjectives that exaggerate its attributes, such as 'bold', 'unique' or 'groundbreaking'"))