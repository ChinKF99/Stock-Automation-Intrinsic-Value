import os
import time
import pandas as pd
import requests
from dotenv import load_dotenv

# =====================================================
# STEP 0 - LOAD ENVIRONMENT VARIABLES
# =====================================================

#Looad local .env file if it exists
load_dotenv()

API_KEY = os.environ.get("MY_API_KEY")

if not API_KEY:
    raise ValueError("MY_API_KEY not found in environment variables.")
else:
    print("Success: API key securely loaded.")

