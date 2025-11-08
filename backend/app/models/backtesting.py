"""Backtesting-related Pydantic models"""
from pydantic import BaseModel
from typing import List, Optional


class BacktestConfig(BaseModel):
    """Backtest configuration"""
    jobId: str
    baselineStrategies: Optional[List[str]] = []
    force: bool = False  # Force re-run even if results exist


class BacktestMetrics(BaseModel):
    """Backtest metrics"""
    totalReturn: float
    sharpeRatio: float
    maxDrawdown: float
    volatility: float
    winRate: float


class BacktestResult(BaseModel):
    """Backtest result for a single algorithm"""
    algorithm: str
    type: str  # 'drl' or 'baseline'
    returns: List[float]
    cumulativeReturns: List[float]
    dates: List[str]
    metrics: BacktestMetrics


class BacktestComparison(BaseModel):
    """Comparison of backtest results"""
    bestAlgorithm: str
    bestReturn: float
    bestSharpeRatio: float


class BacktestResponse(BaseModel):
    """Backtest response"""
    jobId: str
    results: List[BacktestResult]
    comparison: BacktestComparison


class BacktestStartResponse(BaseModel):
    """Response when starting backtest"""
    jobId: str

