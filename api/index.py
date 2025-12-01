import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="NIBRASSE")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint for health check
@app.get("/")
async def root():
    return {"status": "NIBRASSE API is running", "version": "1.5.0"}

# Try to import routes (might fail on first cold start)
try:
    from backend.app.api.routes import router as api_router
    app.include_router(api_router, prefix="/api")
    print("✅ Routes imported successfully")
except Exception as e:
    print(f"⚠️ Warning: Could not import routes: {e}")
    
    # Fallback endpoint
    @app.get("/api/health")
    async def health():
        return {"status": "healthy", "error": str(e)}
