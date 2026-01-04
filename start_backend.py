import os
import sys
from pathlib import Path

# Change to the api directory to make imports work properly
api_path = Path(__file__).parent / "backend" / "api" / "src"
os.chdir(api_path)

# Set environment variables to use in-memory services
os.environ["QDRANT_URL"] = ""
os.environ["NEON_HOST"] = "localhost"
os.environ["NEON_PORT"] = "5432"

# Add the current directory to Python path
sys.path.insert(0, str(api_path))

print("Starting the Physical AI Textbook API server...")
print("Using in-memory Qdrant and SQLite for local testing...")

import uvicorn
from main import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)