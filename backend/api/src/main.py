import os
from dotenv import load_dotenv

# Load environment variables from backend directory first
backend_env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', '.env')
load_dotenv(dotenv_path=backend_env_path, override=True)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import the routes using relative import
from .api.routes import include_rag_routes

app = FastAPI(
    title="Physical AI Textbook RAG API",
    description="API for content retrieval from the Physical AI & Humanoid Robotics textbook",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include RAG routes
include_rag_routes(app)

@app.get("/")
async def root():
    return {"message": "Physical AI Textbook RAG API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)