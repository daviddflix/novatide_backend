import os
from dotenv import load_dotenv
import google.generativeai as genai


load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)

# Function to generate response from Gemini AI
def generate_gemini_response(prompt):
    try:
        model = genai.GenerativeModel('gemini-1.0-pro-latest')
        
        # Generate content based on the prompt
        response = model.generate_content(prompt)
        return {'response': response.text, 'success': True}
    except Exception as e:
        print("Error generating response:", e)
        return {'response': None, 'success': False, 'error': str(e)}

