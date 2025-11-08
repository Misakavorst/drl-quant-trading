"""FastAPI application entry point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .config import settings
from .database import db_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="DRL Quantitative Trading API",
    description="Backend API for Deep Reinforcement Learning based quantitative trading",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    try:
        db_manager.start_tunnel()
        logger.info("SSH tunnel started successfully")
        
        # Test database connection
        schema = db_manager.inspect_schema()
        logger.info(f"Database schema inspected: {len(schema['stock'])} columns in stock table")
        logger.info(f"Database schema inspected: {len(schema['stock_price'])} columns in stock_price table")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    db_manager.stop_tunnel()
    logger.info("SSH tunnel stopped")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "DRL Quantitative Trading API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db_manager.execute_query("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


# Import and include routers
from .routers import stocks, training, backtesting
app.include_router(stocks.router, prefix=settings.api_prefix)
app.include_router(training.router, prefix=settings.api_prefix)
app.include_router(backtesting.router, prefix=settings.api_prefix)

