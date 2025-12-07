"""
FastAPI Application Entry Point
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Main FastAPI application for REST API access.
Run with: uvicorn main_api:app --reload
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from analytics_hub_platform.api.routers import create_api_router
from analytics_hub_platform.infrastructure.settings import get_settings
from analytics_hub_platform.infrastructure.db_init import initialize_database
from analytics_hub_platform.config.branding import BRANDING


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    
    Runs on startup and shutdown.
    """
    # Startup
    settings = get_settings()
    initialize_database()
    print(f"🚀 Analytics Hub API started in {settings.environment} mode")
    
    yield
    
    # Shutdown
    print("👋 Analytics Hub API shutting down")


# Create FastAPI app
app = FastAPI(
    title="Sustainable Economic Development Analytics Hub API",
    description="""
    REST API for the Sustainable Economic Development Analytics Hub.
    
    Provides programmatic access to sustainability indicators, KPI data,
    and analytics for the Ministry of Economy and Planning.
    
    ## Features
    
    - **Indicators**: Access sustainability indicator data
    - **Sustainability**: Aggregated sustainability metrics and comparisons
    - **Data Quality**: Data completeness and quality metrics
    - **Reference**: Reference data for regions and time periods
    
    ## Authentication
    
    Production deployment uses SSO integration. For development:
    - Use `X-Tenant-ID` header for tenant context
    - Use `X-User-ID` header for user context
    
    ## Rate Limiting
    
    API requests are rate-limited to 60 requests per minute per user.
    """,
    version="1.0.0",
    contact={
        "name": BRANDING["author_name"],
        "email": BRANDING["author_email"],
    },
    license_info={
        "name": "Proprietary",
        "url": "https://ministry.gov.sa",
    },
    lifespan=lifespan,
)

# CORS middleware
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["https://ministry.gov.sa"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle uncaught exceptions."""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": type(exc).__name__,
        },
    )


# Include API router
api_router = create_api_router()
app.include_router(api_router, prefix="/api/v1")


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Sustainable Economic Development Analytics Hub API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/api/v1/health",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
