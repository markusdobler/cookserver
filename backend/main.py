import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

from .api.import_routes import router as import_router, set_import_service
from .services.import_service import ImportService

# Load environment variables from project root
project_root = Path(__file__).parent.parent
load_dotenv(project_root / ".env")

# Configuration
BASE_PATH = os.getenv("BASE_PATH", "").rstrip("/")
COOK_PATH = os.getenv("COOK_PATH", "cook-toy")
RECIPES_DIR = os.getenv("RECIPES_DIR", "../recipes/import")

# Create FastAPI app
app = FastAPI(
    title="Cook Import Server",
    description="Import recipes from URLs using the cook tool",
    version="1.0.0",
    root_path=BASE_PATH
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize import service
recipes_path = Path(__file__).parent / RECIPES_DIR
import_service = ImportService(
    cook_path=COOK_PATH,
    recipes_dir=str(recipes_path.resolve())
)
set_import_service(import_service)

# Include routers
app.include_router(import_router)


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "base_path": BASE_PATH,
        "cook_path": COOK_PATH,
        "recipes_dir": str(recipes_path.resolve())
    }


# Serve static files from frontend/dist (production build)
# IMPORTANT: This must be registered AFTER all API routes
static_dir = project_root / "frontend" / "dist"
if static_dir.exists():
    # Mount static assets with cache headers
    app.mount("/assets", StaticFiles(directory=static_dir / "assets"), name="assets")
    
    # SPA fallback - serve index.html for all non-API routes
    # This catch-all route must be registered last
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve static files or SPA fallback (excludes /api routes)"""
        # Don't serve static files for API routes
        if full_path.startswith("api/"):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Not Found")
        
        file_path = static_dir / full_path
        
        # If file exists, serve it
        if file_path.is_file():
            # Add cache headers for static assets
            if full_path.startswith("assets/"):
                return FileResponse(
                    file_path,
                    headers={"Cache-Control": "public, max-age=31536000, immutable"}
                )
            return FileResponse(file_path)
        
        # Otherwise serve index.html (SPA routing)
        return FileResponse(static_dir / "index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=7395,
        reload=True
    )
