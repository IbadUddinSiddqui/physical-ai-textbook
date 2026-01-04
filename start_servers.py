import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import subprocess
import threading
import time

def start_backend():
    """Start the backend server with in-memory services"""
    print("Starting backend server...")

    # Load environment variables but override database settings for local testing
    backend_env_path = Path(__file__).parent / "backend" / ".env"
    load_dotenv(dotenv_path=backend_env_path, override=True)

    # Override to use in-memory services
    os.environ["QDRANT_URL"] = ""
    os.environ["QDRANT_HOST"] = "localhost"  # This will use in-memory if URL is empty
    os.environ["NEON_HOST"] = "localhost"  # Will use SQLite for local testing
    os.environ["NEON_PORT"] = "5432"

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

    uvicorn.run(app, host="0.0.0.0", port=8000)

def start_frontend():
    """Start the frontend server"""
    print("Starting frontend server...")

    frontend_path = Path(__file__).parent / "frontend" / "docusaurus"
    os.chdir(frontend_path)

    # Run npm start command
    subprocess.run(["npx", "docusaurus", "start"], shell=True)

if __name__ == "__main__":
    print("Starting both backend and frontend servers...")
    print("Backend will run on http://localhost:8000")
    print("Frontend will run on http://localhost:3000")

    # Start backend in a separate thread
    backend_thread = threading.Thread(target=start_backend)
    backend_thread.daemon = True
    backend_thread.start()

    # Give backend a moment to start
    time.sleep(2)

    # Start frontend
    start_frontend()