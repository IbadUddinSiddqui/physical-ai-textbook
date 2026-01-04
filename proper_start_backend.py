import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from the backend .env file
backend_env_path = Path(__file__).parent / "backend" / ".env"
load_dotenv(dotenv_path=backend_env_path, override=True)

# Change to the api directory to make imports work properly
api_path = Path(__file__).parent / "backend" / "api" / "src"
os.chdir(api_path)

# Add the current directory to Python path
sys.path.insert(0, str(api_path))

print("Starting the Physical AI Textbook API server...")
print(f"GEMINI_API_KEY loaded: {'Yes' if os.getenv('GEMINI_API_KEY') else 'No'}")
print(f"Using model: {os.getenv('GEMINI_CHAT_MODEL', 'gemini-2.5-flash')}")

import uvicorn
from main import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)