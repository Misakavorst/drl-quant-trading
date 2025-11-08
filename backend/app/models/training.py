"""Training-related Pydantic models"""
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum


class TrainingStatus(str, Enum):
    """Training status enum"""
    PENDING = "pending"
    TRAINING = "training"
    COMPLETED = "completed"
    FAILED = "failed"


class TrainingConfig(BaseModel):
    """Training configuration request"""
    symbols: List[str]
    algorithms: List[str]
    startDate: Optional[str] = None  # Format: YYYY-MM-DD
    endDate: Optional[str] = None    # Format: YYYY-MM-DD
    trainTestSplit: Optional[float] = None  # Default will use settings value
    totalTimesteps: Optional[int] = None  # Total training timesteps, default will use settings value


class TrainingProgress(BaseModel):
    """Training progress for a single algorithm"""
    algorithm: str
    epoch: int
    totalEpochs: int
    loss: float
    reward: float
    status: TrainingStatus


class TrainingMetrics(BaseModel):
    """Training metrics"""
    totalReward: float
    sharpeRatio: float
    maxDrawdown: float
    winRate: float
    initialAmount: float = 1000000.0  # Initial capital
    finalAmount: float = 0.0  # Final portfolio value
    returnRate: float = 0.0  # Return rate as percentage


class TrainingResult(BaseModel):
    """Training result for a single algorithm"""
    algorithm: str
    status: str
    metrics: TrainingMetrics
    trainingTime: float
    modelPath: str


class TrainingResponse(BaseModel):
    """Training response with progress and results"""
    jobId: str
    progress: List[TrainingProgress]
    results: List[TrainingResult]


class TrainingStartResponse(BaseModel):
    """Response when starting training"""
    jobId: str

