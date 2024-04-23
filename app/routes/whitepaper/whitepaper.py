from flask import Blueprint, request, jsonify
from sqlalchemy import func
from config import WhitepaperAnalysis, session
from app.services.Perplexity.perplexity import perplexity_api_request
from app.services.OpenAI.openAI import ask_chatgpt
import threading
from app.routes.whitepaper.perplexity_helpers import general_perplexity_prompt
from app.routes.whitepaper.perplexity_helpers import pre_competitor_perplexity_prompt
from app.routes.whitepaper.perplexity_helpers import post_competitor_perplexity_prompt
from app.routes.whitepaper.perplexity_helpers import community_perplexity_prompt
from app.routes.whitepaper.perplexity_helpers import platform_and_data_perplexity_prompt
from app.routes.whitepaper.perplexity_helpers import tokenomics_perplexity_prompt
from app.routes.whitepaper.perplexity_helpers import circulating_supply_perplexity_prompt
from app.routes.whitepaper.perplexity_helpers import revenue_perplexity_prompt
from app.routes.whitepaper.perplexity_helpers import team_perplexity_prompt
from app.routes.whitepaper.perplexity_helpers import partners_and_investors_prompt
from app.routes.whitepaper.perplexity_helpers import final_summary_prompt
from app.routes.whitepaper.perplexity_helpers import clean_summary


whitepaper_bp = Blueprint('whitepaperRoutes', __name__)

# ----- CREATE A NEW WHITEPAPER ANALYSIS ROUTE ----- #



@whitepaper_bp.route('/create_whitepaper_analysis', methods=['POST'])
def create_whitepaper_analysis():
    data = request.json
    summary = ""
    perplexity_model = 'sonar-medium-online'

    if not data or 'label' not in data or 'summary' not in data:
        return jsonify({'error': 'Label and summary are required fields', 'success': False}), 400

    pdf_text = data.get('pdfText')
    summary = data.get('summary') if not pdf_text else f'{data["summary"]} {pdf_text}'

    model_prompt_map = {
    'general': general_perplexity_prompt,
    'competitor': f'{pre_competitor_perplexity_prompt}{data["label"]}{post_competitor_perplexity_prompt}',
    'community': community_perplexity_prompt,
    'platform_and_data': platform_and_data_perplexity_prompt,
    'tokenomics': tokenomics_perplexity_prompt,
    'circulating_supply': circulating_supply_perplexity_prompt,
    'revenue': revenue_perplexity_prompt,
    'team': team_perplexity_prompt,
    'partners_and_investors': partners_and_investors_prompt
    }

    try:
        result_container = []

        threads = []
        for prompt in model_prompt_map.values():
            thread = threading.Thread(
                target=process_summary,
                kwargs={'model': 'sonar-medium-online', 'content': summary, 'prompt': prompt, 'result_container': result_container}
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Combine results
        final_summary = (
            f"General Summary \n{result_container[0]}\n"
            f"Competitor Summary \n{result_container[1]}\n"
            f"Community Summary \n{result_container[2]}\n"
            f"Platform Data Summary \n{result_container[3]}\n"
            f"Tokenomics Summary \n{result_container[4]}\n"
            f"Circulating Supply Summary \n{result_container[5]}\n"
            f"Revenue Summary \n{result_container[6]}\n"
            f"Team Summary \n{result_container[7]}\n"
            f"Partners and Investors Summary \n{result_container[8]}\n"
        )

        new_whitepaper = WhitepaperAnalysis(
            label=data['label'],
            perplexity_summary=final_summary,
            open_ai_summary=result_container[0]
        )
        session.add(new_whitepaper)
        session.commit()

        return jsonify({'message': 'Whitepaper analysis created successfully', 'success': True}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'error': f'Error analysing whitepaper {str(e)}', 'success': False}), 500

def process_summary(model, content, prompt, result_container):
    result = perplexity_api_request(model, content=content, prompt=prompt)
    result_container.append(clean_summary(result))



# ----- DELETE A WHITEPAPER ANALYSIS ROUTE ----- #

@whitepaper_bp.route('/delete_whitepaper_analysis', methods=['DELETE'])
def delete_whitepaper_analysis():
    analysis_id = request.args.get('id')
    label = request.args.get('label')

    if not analysis_id and not label:
        return jsonify({'error': 'Query parameter id or label is required', 'success': False}), 400

    try:
        if analysis_id:
            deleted_row = session.query(
                WhitepaperAnalysis).filter_by(id=analysis_id).first()
            if not deleted_row:
                return jsonify({'error': 'Whitepaper analysis not found', 'success': False}), 404
            session.delete(deleted_row)
        elif label:
            deleted_row = session.query(
                WhitepaperAnalysis).filter_by(label=label).first()
            if not deleted_row:
                return jsonify({'error': 'Whitepaper analysis not found', 'success': False}), 404
            session.delete(deleted_row)

        session.commit()
        return jsonify({'message': 'Whitepaper analysis deleted successfully', 'success': True}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e), 'success': False}), 500


# ----- GET ALL WHITEPAPERS ROUTE ----- #

@whitepaper_bp.route('/get_whitepapers', methods=['GET'])
def get_whitepapers():
  try:
    whitepapers = session.query(WhitepaperAnalysis).all()
    return jsonify({'whitepapers': [whitepaper.to_dict() for whitepaper in whitepapers]}), 200
  except Exception as e:
    return jsonify({'error': str(e), 'success': False}), 500


# ----- GET A SINGLE WHITEPAPER ROUTE ----- #

@whitepaper_bp.route('/get_whitepaper', methods=['GET'])
def get_whitepaper():
  analysis_id = request.args.get('id')
  label = request.args.get('label')

  if not analysis_id and not label:
    return jsonify({'error': 'Query parameter id or label is required', 'success': False}), 400

  try:
    if analysis_id:
      whitepaper = session.query(WhitepaperAnalysis).filter_by(id=analysis_id).first()
    elif label:
      # Perform a case-insensitive search for the label
      whitepaper = session.query(WhitepaperAnalysis).filter(
          func.lower(WhitepaperAnalysis.label) == label.lower()  # Convert both to lowercase for comparison
      ).first()

    if not whitepaper:
      return jsonify({'error': 'Whitepaper analysis not found', 'success': False}), 404

    return jsonify(whitepaper.to_dict()), 200

  except Exception as e:
    return jsonify({'error': str(e), 'success': False}), 400
