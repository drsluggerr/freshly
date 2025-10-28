from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.api.endpoints import auth, inventory, receipts, meals, shopping, analytics
import os

app = FastAPI(
    title=settings.APP_NAME,
    description="ADHD-Friendly Pantry & Fridge Inventory Management System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directories
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.RECEIPTS_DIR, exist_ok=True)

# Mount static files for receipts
if os.path.exists(settings.RECEIPTS_DIR):
    app.mount("/receipts", StaticFiles(directory=settings.RECEIPTS_DIR), name="receipts")

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(inventory.router, prefix=f"{settings.API_V1_STR}/inventory", tags=["Inventory"])
app.include_router(receipts.router, prefix=f"{settings.API_V1_STR}/receipts", tags=["Receipts"])
app.include_router(meals.router, prefix=f"{settings.API_V1_STR}/meals", tags=["Meals"])
app.include_router(shopping.router, prefix=f"{settings.API_V1_STR}/shopping", tags=["Shopping"])
app.include_router(analytics.router, prefix=f"{settings.API_V1_STR}/analytics", tags=["Analytics"])


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Freshly API",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
