"""Backtesting API endpoints"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
import logging

from ..models.backtesting import (
    BacktestConfig,
    BacktestStartResponse,
    BacktestResponse,
    BacktestResult,
    BacktestMetrics,
    BacktestComparison
)
from ..services.backtest_service import backtest_service
from ..utils.storage import load_json, job_exists

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/backtesting", tags=["backtesting"])


def run_backtest_job(job_id: str, baseline_strategies: list):
    """Background task to run backtest"""
    try:
        logger.info(f"Starting background backtest for job {job_id}")
        backtest_service.run_backtest(job_id, baseline_strategies)
        logger.info(f"Completed background backtest for job {job_id}")
    except Exception as e:
        logger.error(f"Error in backtest job: {e}", exc_info=True)


@router.post("/start", response_model=BacktestStartResponse)
async def start_backtest(
    request: BacktestConfig,
    background_tasks: BackgroundTasks
):
    """Start backtesting"""
    try:
        job_id = request.jobId
        
        logger.info(f"Starting backtest for job {job_id}")
        
        if not job_exists(job_id):
            raise HTTPException(status_code=404, detail=f"Training job {job_id} not found")
        
        # Check if backtest already exists (unless force=True)
        from ..utils.storage import get_job_dir
        job_dir = get_job_dir(job_id)
        backtest_results_file = job_dir / "backtest_results.json"
        
        if request.force and backtest_results_file.exists():
            # Delete existing results if force re-run
            backtest_results_file.unlink()
            logger.info(f"Deleted existing backtest results for force re-run: {job_id}")
        
        if not backtest_results_file.exists():
            # Only run backtest if results don't exist
            background_tasks.add_task(
                run_backtest_job,
                job_id,
                request.baselineStrategies
            )
            logger.info(f"Queued backtest job for {job_id}")
        else:
            logger.info(f"Backtest results already exist for {job_id}, skipping")
        
        return BacktestStartResponse(jobId=job_id)
        
    except Exception as e:
        logger.error(f"Error starting backtest: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/results/{job_id}", response_model=BacktestResponse)
async def get_backtest_results(job_id: str):
    """Get backtest results"""
    try:
        if not job_exists(job_id):
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        # Load backtest results
        backtest_data = load_json(job_id, "backtest_results.json")
        
        # Convert to response model
        results = [
            BacktestResult(
                algorithm=r["algorithm"],
                type=r["type"],
                returns=r["returns"],
                cumulativeReturns=r["cumulativeReturns"],
                dates=r["dates"],
                metrics=BacktestMetrics(**r["metrics"])
            )
            for r in backtest_data["results"]
        ]
        
        comparison = BacktestComparison(**backtest_data["comparison"])
        
        return BacktestResponse(
            jobId=job_id,
            results=results,
            comparison=comparison
        )
        
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Backtest results not found for job {job_id}. Please run backtest first."
        )
    except Exception as e:
        logger.error(f"Error getting backtest results: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

