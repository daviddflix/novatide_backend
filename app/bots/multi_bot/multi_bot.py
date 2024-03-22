from app.services.openAI.openAI import ask_chatgpt
from app.services.perplexity.perplexity import perplexity_api_request
from app.services.coingecko.actions import get_token_data
from app.services.staking_reward.actions import get_staking_rewards_data
from app.services.coinMarketCap.coinmarketcap import get_crypto_metadata
from app.services.defillama.defillama import get_protocol_tvl, get_llama_chains


def activate_ip_bot(token_name, analysis_prompt):

    if not token_name:
        return {'response': 'Token name is required', 'success': False}
    
    formatted_token_name = str(token_name).casefold()
    coin_analysis_prompt = f"Write a short paragraph (maximum 400 characters) explaining the {formatted_token_name} protocol, the problem it is trying to address and its main use cases."
    if analysis_prompt:
        coin_analysis_prompt = str(analysis_prompt).casefold()

    try: 

        gpt_response=ask_chatgpt(coin_analysis_prompt)
        perplexity_response=perplexity_api_request(coin_analysis_prompt)
        coingecko_response=get_token_data(formatted_token_name)

        # if gpt_response['success'] and coingecko_response['success'] and perplexity_response['success']:

        token_symbol = coingecko_response['symbol'] if coingecko_response['success'] else formatted_token_name
        
        staking_reward_response = get_staking_rewards_data(token_symbol)
        coinmarketcap_response = get_crypto_metadata(token_symbol)
        defillama_response = get_protocol_tvl(token_symbol)
        defillama_chains_response = get_llama_chains(token_symbol)

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
    

