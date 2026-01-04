import os
from dotenv import load_dotenv

# Try loading from different paths
print("Current working directory:", os.getcwd())
print()

# Try loading from current directory
load_dotenv()
print("GEMINI_API_KEY from current dir:", os.getenv('GEMINI_API_KEY', 'NOT FOUND')[:20] + '...')

print()

# Try loading from backend directory explicitly
load_dotenv('.env')
print("GEMINI_API_KEY from .env:", os.getenv('GEMINI_API_KEY', 'NOT FOUND')[:20] + '...')

print()

# Try loading from backend/.env explicitly
load_dotenv('backend/.env')
print("GEMINI_API_KEY from backend/.env:", os.getenv('GEMINI_API_KEY', 'NOT FOUND')[:20] + '...')

print()

# Print the full key from backend/.env
with open('backend/.env', 'r') as f:
    for line in f:
        if line.startswith('GEMINI_API_KEY='):
            print("Full key from file:", line.strip())
            break