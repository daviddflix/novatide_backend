from flask import Blueprint, request, jsonify
from sqlalchemy import func
from config import WhitepaperAnalysis, session
from app.services.Perplexity.perplexity import perplexity_api_request
from app.services.OpenAI.openAI import ask_chatgpt

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
    perplexity_model = 'codellama-70b-instruct'

    if not data:
        return jsonify({'error': 'Data is required', 'success': False}), 400

    if 'label' not in data or 'summary' not in data:
        return jsonify({'error': 'Label and summary are required fields', 'success': False}), 400

    
     # Perplexity prompt Functions:
    try:
        general_perplexity_result = perplexity_api_request(perplexity_model, content=data['summary'], prompt=general_perplexity_prompt)
        general_summary = clean_summary(general_perplexity_result)

        competitor_perplexity_result = perplexity_api_request(perplexity_model, content=f'{pre_competitor_perplexity_prompt}'+ data['label'] + f'{post_competitor_perplexity_prompt}', prompt=f'{pre_competitor_perplexity_prompt}'+ data['label'] + f'{post_competitor_perplexity_prompt}')
        competitor_summary = clean_summary(competitor_perplexity_result)

        community_perplexity_result = perplexity_api_request(perplexity_model, content=data['summary'], prompt=community_perplexity_prompt)
        community_summary = clean_summary(community_perplexity_result)

        platform_and_data_perplexity_result = perplexity_api_request(perplexity_model, content=data['summary'], prompt=platform_and_data_perplexity_prompt)
        platform_data_summary = clean_summary(platform_and_data_perplexity_result)

        tokenomics_perplexity_result = perplexity_api_request(perplexity_model, content=data['summary'], prompt=tokenomics_perplexity_prompt)
        tokenomics_summary = clean_summary(tokenomics_perplexity_result)

        circulating_supply_perplexity_result = perplexity_api_request(perplexity_model, content=data['summary'], prompt=circulating_supply_perplexity_prompt)
        circulating_supply_summary = clean_summary(circulating_supply_perplexity_result)

        revenue_perplexity_result = perplexity_api_request(perplexity_model, content=data['summary'], prompt=revenue_perplexity_prompt)
        revenue_summary = clean_summary(revenue_perplexity_result)

        team_perplexity_result = perplexity_api_request(perplexity_model, content=data['summary'], prompt=team_perplexity_prompt)
        team_summary = clean_summary(team_perplexity_result)

        partners_and_investors_result = perplexity_api_request(perplexity_model, content=data['summary'], prompt=partners_and_investors_prompt)
        partners_investors_summary = clean_summary(partners_and_investors_result)

        final_summary = (
            f"General Summary:\n{general_summary}\n"
            f"Competitor Summary:\n{competitor_summary}\n"
            f"Community Summary:\n{community_summary}\n"
            f"Platform Data Summary:\n{platform_data_summary}\n"
            f"Tokenomics Summary:\n{tokenomics_summary}\n"
            f"Circulating Supply Summary:\n{circulating_supply_summary}\n"
            f"Revenue Summary:\n{revenue_summary}\n"
            f"Team Summary:\n{team_summary}\n"
            f"Partners and Investors Summary:\n{partners_investors_summary}\n"
        )
    
        
        new_whitepaper = WhitepaperAnalysis(
        label=data['label'],
        perplexity_summary=final_summary,
        open_ai_summary=general_summary
        )
        session.add(new_whitepaper)
        session.commit()


        return jsonify({'message': 'Whitepaper analysis created successfully', 'success': True}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'ERROR': f' ERROR PERPLEXITY {str(e)}', 'success': False}), 500


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
