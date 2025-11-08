"""Stock management API endpoints"""
from fastapi import APIRouter, HTTPException, Query
from typing import List
import logging

from ..models.stock import (
    StockListRequest,
    StockListResponse,
    StockData
)
from ..services.data_service import data_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.post("/add", response_model=StockListResponse)
async def add_stocks(request: StockListRequest):
    """
    Add stocks and fetch data from database
    Returns sample data (first 20 rows) for display
    """
    try:
        logger.info(f"Fetching data for symbols: {request.symbols}")
        logger.info(f"Date range: {request.startDate} to {request.endDate}")
        
        # Fetch and prepare data
        data = data_service.fetch_and_prepare_data(
            symbols=request.symbols,
            start_date=request.startDate,
            end_date=request.endDate
        )
        
        # Convert raw data to StockData models
        stock_data_list = [StockData(**item) for item in data['raw_data']]
        
        return StockListResponse(
            data=stock_data_list,
            total=len(data['dates']),
            symbols=data['symbols'],
            dateRange={
                "start": request.startDate,
                "end": request.endDate
            }
        )
    
    except ValueError as e:
        logger.error(f"Value error: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding stocks: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=List[dict])
async def get_stock_list(search: str = Query(None, description="Search term")):
    """
    Get list of available stocks (for autocomplete)
    """
    try:
        from ..database import db_manager
        
        # Get all stocks or search by symbol/name
        if search:
            query = """
                SELECT ticker as symbol, name 
                FROM kol.stock 
                WHERE ticker ILIKE %s OR name ILIKE %s
                ORDER BY ticker
                LIMIT 50
            """
            search_term = f"%{search}%"
            stocks = db_manager.execute_query(query, (search_term, search_term))
        else:
            query = """
                SELECT ticker as symbol, name 
                FROM kol.stock 
                ORDER BY ticker
                LIMIT 100
            """
            stocks = db_manager.execute_query(query)
        
        return [{"value": s['symbol'], "label": f"{s['symbol']} - {s.get('name', '')}"} for s in stocks]
        
    except Exception as e:
        logger.error(f"Error getting stock list: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sample", response_model=StockListResponse)
async def get_sample_data(
    symbols: str = Query(..., description="Comma-separated stock symbols"),
    startDate: str = Query(..., description="Start date (YYYY-MM-DD)"),
    endDate: str = Query(..., description="End date (YYYY-MM-DD)")
):
    """
    Get sample stock data for display
    """
    try:
        symbol_list = [s.strip() for s in symbols.split(',')]
        
        logger.info(f"Getting sample data for: {symbol_list}")
        
        # Get all data (no limit)
        sample_data = data_service.get_sample_data(
            symbols=symbol_list,
            start_date=startDate,
            end_date=endDate,
            limit=None
        )
        
        stock_data_list = [StockData(**item) for item in sample_data]
        
        return StockListResponse(
            data=stock_data_list,
            total=len(sample_data),
            symbols=symbol_list,
            dateRange={
                "start": startDate,
                "end": endDate
            }
        )
    
    except Exception as e:
        logger.error(f"Error getting sample data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

