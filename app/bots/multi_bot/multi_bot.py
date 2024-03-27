from app.services.openAI.openAI import ask_chatgpt
from app.services.perplexity.perplexity import perplexity_api_request
from app.services.coingecko.actions import get_token_data
from app.services.staking_reward.actions import get_staking_rewards_data
from app.services.coinMarketCap.coinmarketcap import get_crypto_metadata
from app.services.defillama.defillama import get_protocol_tvl, get_llama_chains
from config import session, Token
from datetime import datetime


def get_all_available_data(token_name, analysis_prompt):

    if not token_name:
        return {'response': 'Token name is required', 'success': False}
    
    formatted_token_name = str(token_name).casefold().strip()
  
    coin_analysis_prompt = f"Write a short paragraph (maximum 400 characters) explaining the {formatted_token_name} protocol, the problem it is trying to address and its main use cases."
    if analysis_prompt:
        coin_analysis_prompt = str(analysis_prompt).casefold()

    try: 
        gpt_response=ask_chatgpt(coin_analysis_prompt, model="gpt-4-0125-preview")
        perplexity_response=perplexity_api_request(coin_analysis_prompt, "codellama-70b-instruct")
        coingecko_response=get_token_data(formatted_token_name)

        token_symbol = coingecko_response['symbol'] if coingecko_response['success'] else formatted_token_name
        
        staking_reward_response = get_staking_rewards_data(token_symbol)
        coinmarketcap_response = get_crypto_metadata(token_symbol)
        defillama_response = get_protocol_tvl(token_symbol)
        defillama_chains_response = get_llama_chains(token_symbol)

        token = session.query(Token).filter_by(gecko_id=formatted_token_name).first()
        if token:
            if gpt_response['success']:
                token.analysis_1 = gpt_response['response']
            if perplexity_response['success']:
                token.analysis_2 = perplexity_response['response']
            if coinmarketcap_response['success']:
                token.whitepaper = coinmarketcap_response['whitepaper']
            if defillama_chains_response['success']:
                token.tvl = defillama_chains_response['tvl']
            if staking_reward_response['success']:
                token.inflation_rate = staking_reward_response['inflation_rate']
                token.reward_rate = staking_reward_response['reward_rate']
                token.annualized_revenue_fee = staking_reward_response['annualized_revenue_fee']
            if coingecko_response['success']:
                token.ath = coingecko_response['ath']
                token.logo = coingecko_response['logo']
                token.market_cap_usd = coingecko_response['market_cap_usd']
                token.total_volume = coingecko_response['total_volume']
                token.website = coingecko_response['website']
                token.total_supply = coingecko_response['total_supply']
                token.circulating_supply = coingecko_response['circulating_supply']
                token.percentage_circulating_supply = coingecko_response['percentage_circulating_supply']
                token.max_supply = coingecko_response['max_supply']
                token.supply_model = coingecko_response['supply_model']
                token.current_price = coingecko_response['current_price']
                token.price_a_year_ago = coingecko_response['price_a_year_ago']
                token.price_change_percentage_1y = coingecko_response['price_change_percentage_1y']
                token.ath_change_percentage = coingecko_response['ath_change_percentage']
                token.coingecko_link = coingecko_response['coingecko_link']
                token.categories = coingecko_response['categories']
                token.chains = coingecko_response['chains']
                token.contracts = coingecko_response['contracts']
                token.description = coingecko_response['description']
                token.fully_diluted_valuation = coingecko_response['fully_diluted_valuation']
                token.updated_at = datetime.now()
                
            session.commit()

        final_response = {
            'analysis_1': gpt_response,
            'analysis_2': perplexity_response,
            'coingecko_response': coingecko_response,
            'staking_reward_response': staking_reward_response,
            'coinmarketcap_response': coinmarketcap_response,
            'defillama_protocol_response': defillama_response,
            'defillama_chains_response': defillama_chains_response,
        }
        return {'response': final_response, 'success': True}
    
    except Exception as e:
        return {'response': str(e), 'success': False}
    

def activate_multi_bot():
    try:
        tokens = session.query(Token).order_by(Token.created_at).all()
        
        ids = []
        for token in tokens:
            ids.append(token.gecko_id)

        if ids:
            print('IDs:', ids)
            for id in ids:
                coingecko_response=get_token_data(id)
                token = session.query(Token).filter_by(gecko_id=id).first()
                if coingecko_response['success']:
                    token.ath = coingecko_response['ath']
                    token.logo = coingecko_response['logo']
                    token.market_cap_usd = coingecko_response['market_cap_usd']
                    token.total_volume = coingecko_response['total_volume']
                    token.website = coingecko_response['website']
                    token.total_supply = coingecko_response['total_supply']
                    token.circulating_supply = coingecko_response['circulating_supply']
                    token.percentage_circulating_supply = coingecko_response['percentage_circulating_supply']
                    token.max_supply = coingecko_response['max_supply']
                    token.supply_model = coingecko_response['supply_model']
                    token.current_price = coingecko_response['current_price']
                    token.price_a_year_ago = coingecko_response['price_a_year_ago']
                    token.price_change_percentage_1y = coingecko_response['price_change_percentage_1y']
                    token.ath_change_percentage = coingecko_response['ath_change_percentage']
                    token.coingecko_link = coingecko_response['coingecko_link']
                    token.categories = coingecko_response['categories']
                    token.chains = coingecko_response['chains']
                    token.contracts = coingecko_response['contracts']
                    token.fully_diluted_valuation = coingecko_response['fully_diluted_valuation']
                    token.updated_at = datetime.now()
                session.commit()
            return {'response': 'Tokens updated', 'success': True}
        else:
            return {'response': 'No tokens to analyse', 'success': False}

    except Exception as e:
        session.rollback()
        return {'error': str(e), 'success': False}