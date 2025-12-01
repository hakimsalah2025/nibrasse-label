import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routes from backend
from backend.app.api.routes import router as api_router

app = FastAPI(title="NIBRASSE")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router, prefix="/api")

# Root endpoint for health check
@app.get("/")
async def root():
    return {"status": "NIBRASSE API is running", "version": "1.5.0"}
