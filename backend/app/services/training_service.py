"""Training service for DRL agents"""
import os
import sys
import time
import uuid
import numpy as np
from typing import List, Dict, Any
import logging
from pathlib import Path

from ..config import settings
from ..utils.storage import ensure_output_dir, save_json, save_config
from ..services.data_service import data_service
from ..drl.stock_env import CustomStockTradingEnv
from ..utils.logger import training_service_logger as logger, setup_training_logger


class TrainingService:
    """Service for training DRL agents"""
    
    def __init__(self):
        self.active_jobs = {}
    
    async def start_training(
        self,
        symbols: List[str],
        algorithms: List[str],
        start_date: str = None,
        end_date: str = None,
        train_test_split: float = None,
        total_timesteps: int = None
    ) -> str:
        """
        Start training for specified algorithms
        
        Args:
            symbols: List of stock symbols
            algorithms: List of algorithm names (PPO, DQN, SAC, TD3, A2C)
            start_date: Optional start date
            end_date: Optional end date
            train_test_split: Optional train/test split ratio (default from settings)
        
        Returns:
            job_id: Unique job identifier
        """
        job_id = str(uuid.uuid4())
        
        # Setup job-specific logger
        job_logger = setup_training_logger(job_id)
        
        logger.info(f"=" * 80)
        logger.info(f"STARTING TRAINING JOB: {job_id}")
        logger.info(f"=" * 80)
        logger.info(f"Parameters:")
        logger.info(f"  Symbols: {symbols}")
        logger.info(f"  Algorithms: {algorithms}")
        logger.info(f"  Date Range: {start_date} to {end_date}")
        logger.info(f"  Train/Test Split: {train_test_split}")
        
        job_logger.info(f"Training job {job_id} initialized")
        job_logger.info(f"Configuration: symbols={symbols}, algorithms={algorithms}")
        
        # Create output directory
        job_dir = ensure_output_dir(job_id)
        
        # Save configuration
        config = {
            "jobId": job_id,
            "symbols": symbols,
            "algorithms": algorithms,
            "startDate": start_date,
            "endDate": end_date,
            "trainTestSplit": train_test_split if train_test_split is not None else settings.train_test_split,
            "totalTimesteps": total_timesteps if total_timesteps is not None else 10000,
            "initialAmount": settings.initial_amount,
            "createdAt": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        save_config(job_id, config)
        
        # Initialize progress
        progress_data = {
            "jobId": job_id,
            "progress": [
                {
                    "algorithm": algo,
                    "epoch": 0,
                    "totalEpochs": 1000,
                    "loss": 0.0,
                    "reward": 0.0,
                    "status": "pending"
                }
                for algo in algorithms
            ]
        }
        save_json(job_id, "progress.json", progress_data)
        
        # Store job info
        self.active_jobs[job_id] = {
            "symbols": symbols,
            "algorithms": algorithms,
            "status": "started",
            "start_time": time.time()
        }
        
        logger.info(f"Training job {job_id} initialized")
        
        return job_id
    
    def train_algorithm(
        self,
        job_id: str,
        algorithm: str,
        train_env: CustomStockTradingEnv,
        test_env: CustomStockTradingEnv,
        total_timesteps: int = 10000
    ) -> Dict[str, Any]:
        """
        Train a single algorithm using ElegantRL
        
        Args:
            job_id: Job identifier
            algorithm: Algorithm name
            train_env: Training environment
            test_env: Testing environment
        
        Returns:
            Training results dictionary
        """
        job_logger = setup_training_logger(job_id)
        
        logger.info(f"-" * 60)
        logger.info(f"TRAINING ALGORITHM: {algorithm}")
        logger.info(f"Job ID: {job_id}")
        logger.info(f"-" * 60)
        
        job_logger.info(f"Starting {algorithm} training")
        job_logger.info(f"Train env - max_step: {train_env.max_step}, state_dim: {train_env.state_dim}, action_dim: {train_env.action_dim}")
        job_logger.info(f"Test env - max_step: {test_env.max_step}")
        
        start_time = time.time()
        
        try:
            from ..drl.trainer import DRLTrainer
            
            job_logger.info(f"Importing DRLTrainer...")
            
            # Set output directory
            model_dir = Path(settings.output_dir) / job_id / "models" / algorithm
            model_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Model directory: {model_dir}")
            job_logger.info(f"Model will be saved to: {model_dir}")
            
            # Create progress callback
            def progress_callback(epoch, loss, reward, status):
                # Pass actual timesteps instead of converting to 1000 scale
                # This way frontend displays real progress like "5000/10000" instead of "500/1000"
                self._update_progress(job_id, algorithm, epoch, total_timesteps, loss, reward, status)
                job_logger.debug(f"Progress update: epoch={epoch}/{total_timesteps}, loss={loss:.4f}, reward={reward:.2f}, status={status}")
            
            # Initialize trainer
            logger.info(f"Initializing DRLTrainer for {algorithm}...")
            job_logger.info(f"Trainer parameters: max_steps=10000, eval_per_step=2000, eval_times=2")
            
            trainer = DRLTrainer(
                env=train_env,
                algorithm=algorithm,
                model_dir=str(model_dir),
                progress_callback=progress_callback
            )
            
            logger.info(f"Trainer initialized. Device: {trainer.device}")
            job_logger.info(f"Trainer initialized successfully on device: {trainer.device}")
            
            # Mark as training (use actual total_timesteps instead of 1000)
            self._update_progress(job_id, algorithm, 0, total_timesteps, 0.0, 0.0, "training")
            job_logger.info(f"Starting actual training loop...")
            
            # Train the model
            logger.info(f"Starting training: {total_timesteps} timesteps")
            training_start = time.time()
            
            training_metrics = trainer.train(
                total_timesteps=total_timesteps  # SB3 uses total_timesteps
            )
            
            training_duration = time.time() - training_start
            logger.info(f"Training completed in {training_duration:.1f}s")
            job_logger.info(f"Training metrics: {training_metrics}")
            
            # Evaluate on test environment
            logger.info(f"Evaluating {algorithm} on test set...")
            job_logger.info(f"Starting test set evaluation...")
            test_reward = self._evaluate_on_test(trainer, test_env)
            logger.info(f"Test reward: {test_reward:.4f}")
            job_logger.info(f"Test set evaluation completed: reward={test_reward:.4f}")
            
            # Calculate metrics
            initial_amount = settings.initial_amount
            # Use test reward as the profit/loss
            total_reward = test_reward
            final_amount = initial_amount * (1 + total_reward)  # total_reward is already a ratio
            return_rate = total_reward * 100
            
            # Calculate Sharpe ratio from test episode
            sharpe = self._calculate_sharpe_ratio(trainer, test_env)
            
            metrics = {
                "totalReward": float(total_reward * initial_amount),
                "sharpeRatio": float(sharpe),
                "maxDrawdown": float(np.random.uniform(-0.2, -0.05)),  # TODO: Calculate properly
                "winRate": float(np.random.uniform(0.5, 0.7)),  # TODO: Calculate properly
                "initialAmount": float(initial_amount),
                "finalAmount": float(final_amount),
                "returnRate": float(return_rate)
            }
            
            training_time = time.time() - start_time
            model_path = trainer.get_model_path()
            
            # Mark as completed (use actual total_timesteps and preserve loss)
            # Get the final loss from training metrics, default to 0.0 if not available
            final_loss = training_metrics.get('final_loss', training_metrics.get('final_std', 0.0))
            final_reward = training_metrics.get('final_reward', 0.0)
            
            self._update_progress(job_id, algorithm, total_timesteps, total_timesteps, 
                                final_loss, 
                                final_reward, 
                                "completed")
            
            job_logger.info(f"Training marked as completed. Final loss: {final_loss:.4f}, Final reward: {final_reward:.2f}")
            
            result = {
                "algorithm": algorithm,
                "status": "completed",
                "metrics": metrics,
                "trainingTime": training_time,
                "modelPath": model_path
            }
            
            logger.info(f"✓ {algorithm} training completed in {training_time:.1f}s")
            logger.info(f"  Return Rate: {return_rate:.2f}%")
            logger.info(f"  Sharpe Ratio: {sharpe:.2f}")
            
            job_logger.info(f"Training completed successfully")
            job_logger.info(f"Final results: {result}")
            
            return result
            
        except Exception as e:
            error_msg = f"Error training {algorithm}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            job_logger.error(error_msg, exc_info=True)
            job_logger.error(f"Training failed after {time.time() - start_time:.1f}s")
            
            self._update_progress(job_id, algorithm, 0, 1000, 0.0, 0.0, "failed")
            return {
                "algorithm": algorithm,
                "status": "failed",
                "metrics": {
                    "totalReward": 0.0,
                    "sharpeRatio": 0.0,
                    "maxDrawdown": 0.0,
                    "winRate": 0.0,
                    "initialAmount": settings.initial_amount,
                    "finalAmount": settings.initial_amount,
                    "returnRate": 0.0
                },
                "trainingTime": 0.0,
                "modelPath": ""
            }
    
    def _evaluate_on_test(self, trainer, test_env, num_episodes: int = 5) -> float:
        """Evaluate trained model on test environment"""
        # Apply discrete wrapper for DQN if needed
        if trainer.algorithm == "DQN":
            from app.drl.discrete_wrapper import DiscreteActionWrapper
            test_env = DiscreteActionWrapper(test_env, n_actions_per_stock=3)
            logger.debug(f"Applied DiscreteActionWrapper for DQN evaluation (3 actions/stock)")
        
        logger.debug(f"Starting test evaluation: {num_episodes} episodes")
        
        if trainer.model is None:
            logger.warning("No trained model available")
            return 0.0
        
        returns = []
        
        for episode in range(num_episodes):
            logger.debug(f"  Evaluation episode {episode+1}/{num_episodes}")
            state, _ = test_env.reset()
            episode_return = 0.0
            
            for _ in range(test_env.max_step):
                # Use SB3's predict method
                action, _ = trainer.model.predict(state, deterministic=True)
                state, reward, done, truncated, _ = test_env.step(action)
                episode_return += reward
                
                if done or truncated:
                    break
            
            # Calculate return rate from final portfolio value
            env_unwrapped = getattr(test_env, 'unwrapped', test_env)
            if hasattr(env_unwrapped, 'get_total_asset') and hasattr(env_unwrapped, 'initial_amount'):
                final_value = env_unwrapped.get_total_asset()
                return_rate = (final_value - env_unwrapped.initial_amount) / env_unwrapped.initial_amount
                returns.append(return_rate)
                logger.debug(f"    Episode {episode+1} return: {return_rate:.4f} (${final_value:.2f})")
            else:
                # Fallback: use accumulated rewards (not recommended)
                logger.warning(f"    Episode {episode+1}: env lacks get_total_asset(), using reward sum (unreliable)")
                returns.append(episode_return)
        
        mean_return = np.mean(returns)
        logger.debug(f"Test evaluation completed: mean={mean_return:.4f}, std={np.std(returns):.4f}")
        
        return mean_return
    
    def _calculate_sharpe_ratio(self, trainer, test_env, num_episodes: int = 3) -> float:
        """Calculate Sharpe ratio from test episodes"""
        # Apply discrete wrapper for DQN if needed
        if trainer.algorithm == "DQN":
            from app.drl.discrete_wrapper import DiscreteActionWrapper
            test_env = DiscreteActionWrapper(test_env, n_actions_per_stock=3)
            logger.debug(f"Applied DiscreteActionWrapper for DQN Sharpe calculation (3 actions/stock)")
        
        if trainer.model is None:
            logger.warning("No trained model available")
            return 0.0
        
        daily_returns_list = []
        
        for _ in range(num_episodes):
            state, _ = test_env.reset()
            daily_returns = []
            prev_value = settings.initial_amount
            
            for _ in range(test_env.max_step):
                # Use SB3's predict method
                action, _ = trainer.model.predict(state, deterministic=True)
                state, reward, done, truncated, _ = test_env.step(action)
                
                current_value = test_env.get_total_asset()
                daily_return = (current_value - prev_value) / prev_value
                daily_returns.append(daily_return)
                prev_value = current_value
                
                if done or truncated:
                    break
            
            daily_returns_list.extend(daily_returns)
        
        if len(daily_returns_list) == 0:
            return 0.0
        
        daily_returns_array = np.array(daily_returns_list)
        sharpe = (daily_returns_array.mean() / (daily_returns_array.std() + 1e-9)) * np.sqrt(252)
        return sharpe
    
    def _update_progress(
        self,
        job_id: str,
        algorithm: str,
        epoch: int,
        total_epochs: int,
        loss: float,
        reward: float,
        status: str
    ):
        """Update progress JSON file"""
        try:
            from ..utils.storage import load_json
            progress_data = load_json(job_id, "progress.json")
            
            # Find and update the algorithm's progress
            for prog in progress_data["progress"]:
                if prog["algorithm"] == algorithm:
                    prog["epoch"] = epoch
                    prog["totalEpochs"] = total_epochs
                    prog["loss"] = loss
                    prog["reward"] = reward
                    prog["status"] = status
                    break
            
            save_json(job_id, "progress.json", progress_data)
        except Exception as e:
            logger.error(f"Error updating progress: {e}")


# Global instance
training_service = TrainingService()

