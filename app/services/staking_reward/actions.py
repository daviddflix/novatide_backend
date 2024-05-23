import requests
from app.services.staking_reward.staking_reward import STAKING_REWARD_BASE_URL, STAKING_REWARD_API_KEY


def get_staking_rewards_data(symbol):
    try:
        symbol = str(symbol).upper()

        query = f"""
            query {{
              assets(where: {{ symbols: ["{symbol}"] }}, limit: 1) {{
                name
                slug
                symbol
                metrics(where: {{ metricKeys: ["reward_rate", "inflation_rate", "fee_revenue"] }}, limit: 10) {{
                  metricKey
                  label
                  defaultValue
                }}
              }}
            }}
        """

        headers = {
            "Content-Type": "application/json",
            "X-API-KEY": STAKING_REWARD_API_KEY,  
        }

        data = {"query": query}

        response = requests.post(STAKING_REWARD_BASE_URL, json=data, headers=headers)
        print('response: ', response.text)

        if response.status_code == 200:
            result = response.json()
            assets = result.get('data', {}).get('assets', [])
            if assets:
                asset = assets[0]
                metrics = asset.get('metrics', [])

                inflation_rate = reward_rate = fee_revenue = None
                for metric in metrics:
                    if metric['metricKey'] == 'inflation_rate':
                        inflation_rate = metric['defaultValue']
                    elif metric['metricKey'] == 'reward_rate':
                        reward_rate = metric['defaultValue']
                    elif metric['metricKey'] == 'fee_revenue':
                        fee_revenue = metric['defaultValue']

                success = all([asset.get('name'), asset.get('slug'), asset.get('symbol'), inflation_rate, reward_rate, fee_revenue])
                return {
                    'inflation_rate': inflation_rate,
                    'reward_rate': reward_rate,
                    'annualized_revenue_fee': fee_revenue,
                    'success': success
                }

            else:
                return {'message': 'No assets found', 'success': False}

        else:
            return {'message': str(response.content), 'status_code': response.status_code, 'success': False}

    except Exception as e:
        return {'message': str(e), 'success': False}



# ---------Example usage------
result = get_staking_rewards_data('stmatic')
print('result: ', result)
    
# ------ Data retrieve-------
# inflation_rate
# reward_rate - APR
# revenue model
