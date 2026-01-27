import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Config:
    #if it has "export UPSTAGE_API_KEY=your_api_key_here", it uses it or we can set it directly in .env file
    UPSTAGE_API_KEY = os.getenv("UPSTAGE_API_KEY")
    SOLAR_BASE_URL = "https://api.upstage.ai/v1"
    # Officially Correct Endpoint for Document Parse
    DOC_PARSE_URL = "https://api.upstage.ai/v1/document-ai/document-parse"
    
    # Model Configuration
    # Using solar-pro3 as it's the most capable for reasoning conform to the prompt
    MODEL_NAME = "solar-pro3" 
