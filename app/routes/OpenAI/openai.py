from flask import Blueprint, request
from app.services.OpenAI.openAI import ask_chatgpt

openai_bp = Blueprint('openai', __name__)

@openai_bp.route('/ask', methods=['POST'])
def ask_openai():
    try:
        model = request.form.get('model')
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