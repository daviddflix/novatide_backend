import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

STAKING_REWARD_API_KEY = os.getenv("STAKING_REWARD_API_KEY")
STAKING_REWARD_BASE_URL = "https://api.stakingrewards.com/public/query"