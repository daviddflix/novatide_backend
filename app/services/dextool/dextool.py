import os
from dotenv import load_dotenv
from dextools_python import DextoolsAPIV2

# Load environment variables from the .env file
load_dotenv()

DEXTOOL_API_KEY = os.getenv("DEXTOOL_API_KEY")
dextools = DextoolsAPIV2(DEXTOOL_API_KEY, plan="standard")