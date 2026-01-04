import os
import sys
from pathlib import Path

# Set the environment variables for local testing
os.environ["QDRANT_URL"] = ""
os.environ["NEON_HOST"] = "localhost"
os.environ["NEON_PORT"] = "5432"

# Change to the api directory to make imports work properly
api_path = Path(__file__).parent / "backend" / "api" / "src"
os.chdir(api_path)

# Add the current directory to Python path
sys.path.insert(0, str(api_path))

print("Starting the Physical AI Textbook API server...")
print("Using in-memory Qdrant and SQLite for local testing...")

# Set environment variables
os.environ["QDRANT_URL"] = ""
os.environ["NEON_HOST"] = "localhost"
os.environ["NEON_PORT"] = "5432"

import uvicorn

if __name__ == "__main__":
    # Import after setting environment
    from main import app
    uvicorn.run(app, host="0.0.0.0", port=8000)