from flask import Blueprint, request
from app.services.openAI import ask

openai_bp = Blueprint('openai', __name__)

@openai_bp.route('/ask', methods=['POST'])
def ask_openai():
    try:
        model = request.form.get('model')
        prompt = request.form.get('prompt')

        if not prompt:
            return 'Prompt needed', 404

        if prompt:
            result = ask(prompt=prompt, model=model)
            return result, 200

    except Exception as e:
        return f"Error in ask to openai route {str(e)}"