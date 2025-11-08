"""Stock-related Pydantic models"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class StockData(BaseModel):
    """Stock price data for a single day"""
    symbol: str
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int


class StockListRequest(BaseModel):
    """Request to add stocks"""
    symbols: List[str]
    startDate: str
    endDate: str


class StockListResponse(BaseModel):
    """Response with stock data"""
    data: List[StockData]
    total: int
    symbols: List[str]
    dateRange: dict


class StockSampleQuery(BaseModel):
    """Query parameters for sample data"""
    symbols: str  # Comma-separated
    startDate: str
    endDate: str

