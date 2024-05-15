from flask import Blueprint, request
from app.services.OpenAI.openAI import ask_chatgpt
from app.services.Perplexity.perplexity import perplexity_api_request
from app.services.Gemini.gemini import generate_gemini_response

ai_bp = Blueprint('openai', __name__)

@ai_bp.route('/ask_gpt', methods=['POST'])
def ask_openai():
    try:
        model = request.form.get('model', 'gpt-4-1106-preview')
        prompt = request.form.get('prompt')

        if not prompt:
            return 'Prompt is required', 404

        result = ask_chatgpt(prompt=prompt, model=model)
        if result['success']:
            return result['response'], 200
        else:
            return result['response'], 500

    except Exception as e:
        return f"Error in ask to openai route {str(e)}", 500
    


@ai_bp.route('/ask_perplexity', methods=['POST'])
def ask_perplexity():
    try:
        model = request.form.get('model', 'codellama-34b-instruct')
        prompt = request.form.get('prompt')
        content = request.form.get('content')
       
        if not content:
            return 'content is required', 404

        result = perplexity_api_request(prompt=prompt, model=model, content=content)
       
        if result['success']:
            return result['response'], 200
        else:
            return result['response'], 500

    except Exception as e:
        return result['response'], 500
    

@ai_bp.route('/generate_gemini_response', methods=['POST'])
def generate_gemini_response_route():
    # Get prompt from request data
    prompt = request.json.get('prompt')

    if not prompt:
        return 'Prompt is required', 404

    # Generate response
    response_data = generate_gemini_response(prompt)

    if response_data['success']:
        return response_data['response'], 200
    else:
        return response_data['error'], 500