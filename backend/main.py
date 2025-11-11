"""
FastAPI Backend for MUSEic
Provides REST API endpoints for the React frontend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from api.routes import generate, transpose, health
from api.models.response import HealthResponse

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="MUSEic API",
    description="The AI tool that turns your lyrical into a miracle",
    version="1.0.0"
)

# CORS configuration
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(generate.router, prefix="/api", tags=["generate"])
app.include_router(transpose.router, prefix="/api", tags=["transpose"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "MUSEic API",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

