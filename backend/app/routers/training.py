"""Training API endpoints"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
import logging
import time
import numpy as np
from pathlib import Path

from ..models.training import (
    TrainingConfig,
    TrainingStartResponse,
    TrainingResponse,
    TrainingProgress,
    TrainingResult,
    TrainingMetrics
)
from ..services.training_service import training_service
from ..services.data_service import data_service
from ..utils.storage import load_json, job_exists, save_json, load_config
from ..config import settings
from ..drl.stock_env import CustomStockTradingEnv

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/training", tags=["training"])


def run_training_job(
    job_id: str,
    symbols: List[str],
    algorithms: List[str],
    start_date: str = None,
    end_date: str = None,
    train_test_split: float = None,
    total_timesteps: int = None
):
    """Background task to run training"""
    try:
        logger.info(f"Starting background training for job {job_id}")
        
        # Use provided dates or defaults
        if not start_date:
            start_date = "2020-01-01"
        if not end_date:
            end_date = "2023-12-31"
        if train_test_split is None:
            train_test_split = settings.train_test_split
        if total_timesteps is None:
            total_timesteps = 10000
        
        # 检查算法特定的最小训练步数建议（基于ElegantRL最佳实践更新）
        # 这些推荐值考虑了learning_starts、buffer_size等参数
        MIN_TIMESTEPS_RECOMMENDED = {
            "PPO": 10000,   # PPO需要足够的episodes来填充rollout buffer (n_steps * n_envs)
            "DQN": 10000,   # DQN需要1000+ steps来开始学习，建议10k+用于稳定训练
            "A2C": 8000,    # A2C需要足够的steps来收集advantages
            "SAC": 15000,   # SAC需要2000+ steps开始学习，建议15k+用于充分探索
            "TD3": 15000,   # TD3需要2000+ steps开始学习，建议15k+用于稳定训练
        }
        
        for algo in algorithms:
            min_steps = MIN_TIMESTEPS_RECOMMENDED.get(algo, 8000)
            if total_timesteps < min_steps:
                logger.warning(
                    f"⚠️ {algo} 建议至少训练 {min_steps} 步，"
                    f"当前仅 {total_timesteps} 步，可能影响训练效果"
                )
        
        logger.info(f"Date range: {start_date} to {end_date}")
        logger.info(f"Train/test split: {train_test_split:.2%}")
        logger.info(f"Total timesteps: {total_timesteps}")
        
        # Fetch data from database
        data = data_service.fetch_and_prepare_data(
            symbols=symbols,
            start_date=start_date,
            end_date=end_date
        )
        
        close_ary = data['close_ary']
        tech_ary = data['tech_ary']
        dates = data['dates']  # Get actual dates from data
        
        # Split train/test
        split_idx = int(len(close_ary) * train_test_split)
        
        logger.info(f"Data split: train={split_idx}, test={len(close_ary)-split_idx}")
        logger.info(f"Train dates: {dates[0]} to {dates[split_idx-1]}")
        logger.info(f"Test dates: {dates[split_idx]} to {dates[-1]}")
        
        # Create environments
        train_env = CustomStockTradingEnv(
            close_ary=close_ary,
            tech_ary=tech_ary,
            initial_amount=settings.initial_amount,
            max_stock=settings.max_stock,
            cost_pct=settings.transaction_cost_pct,
            beg_idx=0,
            end_idx=split_idx
        )
        
        test_env = CustomStockTradingEnv(
            close_ary=close_ary,
            tech_ary=tech_ary,
            initial_amount=settings.initial_amount,
            max_stock=settings.max_stock,
            cost_pct=settings.transaction_cost_pct,
            beg_idx=split_idx,
            end_idx=None
        )
        
        # Save data with dates
        from ..utils.storage import ensure_output_dir
        job_dir = ensure_output_dir(job_id)
        data_dir = job_dir / "data"
        np.savez(
            str(data_dir / "train.npz"),
            close_ary=close_ary[:split_idx],
            tech_ary=tech_ary[:split_idx],
            dates=np.array(dates[:split_idx])
        )
        np.savez(
            str(data_dir / "test.npz"),
            close_ary=close_ary[split_idx:],
            tech_ary=tech_ary[split_idx:],
            dates=np.array(dates[split_idx:])
        )
        
        # Train each algorithm
        results = []
        for algorithm in algorithms:
            result = training_service.train_algorithm(
                job_id=job_id,
                algorithm=algorithm,
                train_env=train_env,
                test_env=test_env,
                total_timesteps=total_timesteps
            )
            results.append(result)
        
        # Save final results
        results_data = {
            "jobId": job_id,
            "results": results
        }
        save_json(job_id, "results.json", results_data)
        
        logger.info(f"Completed training job {job_id}")
        
    except Exception as e:
        logger.error(f"Error in training job {job_id}: {e}", exc_info=True)


@router.post("/start", response_model=TrainingStartResponse)
async def start_training(
    request: TrainingConfig,
    background_tasks: BackgroundTasks
):
    """Start training job"""
    try:
        logger.info(f"Received training request: {request}")
        
        # Start training service
        job_id = await training_service.start_training(
            symbols=request.symbols,
            algorithms=request.algorithms,
            start_date=request.startDate,
            end_date=request.endDate,
            train_test_split=request.trainTestSplit,
            total_timesteps=request.totalTimesteps
        )
        
        # Add background task
        background_tasks.add_task(
            run_training_job,
            job_id,
            request.symbols,
            request.algorithms,
            request.startDate,
            request.endDate,
            request.trainTestSplit,
            request.totalTimesteps
        )
        
        return TrainingStartResponse(jobId=job_id)
        
    except Exception as e:
        logger.error(f"Error starting training: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/progress/{job_id}", response_model=TrainingResponse)
async def get_training_progress(job_id: str):
    """Get training progress"""
    try:
        if not job_exists(job_id):
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        # Load progress
        progress_data = load_json(job_id, "progress.json")
        
        # Load results if available
        try:
            results_data = load_json(job_id, "results.json")
            results = [
                TrainingResult(
                    algorithm=r["algorithm"],
                    status=r["status"],
                    metrics=TrainingMetrics(**r["metrics"]),
                    trainingTime=r["trainingTime"],
                    modelPath=r["modelPath"]
                )
                for r in results_data.get("results", [])
            ]
        except FileNotFoundError:
            results = []
        
        # Convert progress
        progress_list = [
            TrainingProgress(**p)
            for p in progress_data["progress"]
        ]
        
        return TrainingResponse(
            jobId=job_id,
            progress=progress_list,
            results=results
        )
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Progress data not found for job {job_id}")
    except Exception as e:
        logger.error(f"Error getting progress: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/results/{job_id}", response_model=TrainingResponse)
async def get_training_results(job_id: str):
    """Get training results"""
    try:
        if not job_exists(job_id):
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
        
        # Load results
        results_data = load_json(job_id, "results.json")
        progress_data = load_json(job_id, "progress.json")
        
        results = [
            TrainingResult(
                algorithm=r["algorithm"],
                status=r["status"],
                metrics=TrainingMetrics(**r["metrics"]),
                trainingTime=r["trainingTime"],
                modelPath=r["modelPath"]
            )
            for r in results_data["results"]
        ]
        
        progress_list = [
            TrainingProgress(**p)
            for p in progress_data["progress"]
        ]
        
        return TrainingResponse(
            jobId=job_id,
            progress=progress_list,
            results=results
        )
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Results not found for job {job_id}")
    except Exception as e:
        logger.error(f"Error getting results: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=List[dict])
async def get_training_history():
    """Get training history (all completed jobs)"""
    try:
        output_dir = Path(settings.output_dir)
        if not output_dir.exists():
            return []
        
        history = []
        for job_dir in output_dir.iterdir():
            if job_dir.is_dir():
                try:
                    config = load_config(str(job_dir.name))
                    results_file = job_dir / "results.json"
                    
                    job_info = {
                        "jobId": str(job_dir.name),
                        "symbols": config.get("symbols", []),
                        "algorithms": config.get("algorithms", []),
                        "startDate": config.get("startDate"),
                        "endDate": config.get("endDate"),
                        "trainTestSplit": config.get("trainTestSplit"),
                        "createdAt": config.get("createdAt"),
                        "completed": results_file.exists()
                    }
                    
                    history.append(job_info)
                except Exception as e:
                    logger.warning(f"Error loading job {job_dir.name}: {e}")
                    continue
        
        # Sort by creation time, most recent first
        history.sort(key=lambda x: x.get("createdAt", ""), reverse=True)
        
        return history
        
    except Exception as e:
        logger.error(f"Error getting training history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

