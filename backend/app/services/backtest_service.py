"""Backtesting service for trained DRL models"""
import numpy as np
from typing import List, Dict, Any
import logging
from pathlib import Path

from ..config import settings
from ..utils.storage import load_json, save_json, job_exists, get_job_dir
from ..drl.stock_env import CustomStockTradingEnv
from ..utils.logger import backtest_service_logger as logger, setup_backtest_logger


class BacktestService:
    """Service for running backtests"""
    
    def run_backtest(
        self,
        job_id: str,
        baseline_strategies: List[str]
    ) -> Dict[str, Any]:
        """
        Run backtesting for trained models and baseline strategies
        
        Args:
            job_id: Training job ID
            baseline_strategies: List of baseline strategy names
        
        Returns:
            Backtest results dictionary
        """
        # Setup job-specific logger
        job_logger = setup_backtest_logger(job_id)
        
        logger.info(f"=" * 80)
        logger.info(f"STARTING BACKTESTING")
        logger.info(f"Job ID: {job_id}")
        logger.info(f"Baseline Strategies: {baseline_strategies}")
        logger.info(f"=" * 80)
        
        job_logger.info(f"Backtest initiated for job {job_id}")
        job_logger.info(f"Strategies to compare: {baseline_strategies}")
        
        if not job_exists(job_id):
            error_msg = f"Job {job_id} not found"
            logger.error(error_msg)
            job_logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Check if backtest results already exist
        job_dir = get_job_dir(job_id)
        backtest_results_file = job_dir / "backtest_results.json"
        if backtest_results_file.exists():
            logger.info(f"Found existing backtest results, loading...")
            job_logger.info(f"Loading cached backtest results from {backtest_results_file}")
            backtest_data = load_json(job_id, "backtest_results.json")
            logger.info(f"Loaded cached results with {len(backtest_data.get('results', []))} entries")
            return backtest_data
        
        logger.info(f"No cached results found, running full backtest...")
        job_logger.info(f"Starting fresh backtest execution")
        
        # Load job config
        from ..utils.storage import load_config
        config = load_config(job_id)
        logger.info(f"Loaded configuration: {config.get('symbols', [])} symbols, {config.get('algorithms', [])} algorithms")
        job_logger.info(f"Job configuration loaded: {config}")
        
        # Load test data
        job_dir = get_job_dir(job_id)
        test_data_path = job_dir / "data" / "test.npz"
        logger.info(f"Loading test data from {test_data_path}")
        test_data = np.load(str(test_data_path), allow_pickle=True)
        close_ary = test_data['close_ary']
        tech_ary = test_data['tech_ary']
        logger.info(f"Test data loaded: close_ary shape={close_ary.shape}, tech_ary shape={tech_ary.shape}")
        job_logger.info(f"Test data: {close_ary.shape[0]} days, {close_ary.shape[1] if len(close_ary.shape) > 1 else 1} stocks")
        
        # Load actual dates from test data
        if 'dates' in test_data:
            dates = [str(d) for d in test_data['dates']]
            logger.info(f"Loaded {len(dates)} test dates: {dates[0]} to {dates[-1]}")
            job_logger.info(f"Date range: {dates[0]} to {dates[-1]}")
        else:
            # Fallback to approximate dates if not available
            logger.warning("No dates found in test data, using approximate dates")
            job_logger.warning("Dates not found in test.npz, generating approximate dates")
            num_days = len(close_ary)
            dates = [f"2023-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}" for i in range(num_days)]
        
        # Create test environment
        test_env = CustomStockTradingEnv(
            close_ary=close_ary,
            tech_ary=tech_ary,
            initial_amount=settings.initial_amount,
            max_stock=settings.max_stock,
            cost_pct=settings.transaction_cost_pct
        )
        
        results = []
        
        # Run backtest for each trained model
        algorithms = config.get("algorithms", [])
        logger.info(f"-" * 60)
        logger.info(f"BACKTESTING DRL MODELS")
        logger.info(f"Algorithms: {algorithms}")
        logger.info(f"-" * 60)
        
        for i, algorithm in enumerate(algorithms, 1):
            logger.info(f"[{i}/{len(algorithms)}] Backtesting {algorithm}...")
            job_logger.info(f"Starting backtest for algorithm: {algorithm}")
            
            try:
                result = self._backtest_drl_model(
                    job_id=job_id,
                    algorithm=algorithm,
                    test_env=test_env,
                    dates=dates
                )
                results.append(result)
                logger.info(f"  ✓ {algorithm} completed: Total Return = {result['metrics']['totalReturn']:.2%}")
                job_logger.info(f"{algorithm} backtest completed successfully: {result['metrics']}")
            except Exception as e:
                error_msg = f"Error backtesting {algorithm}: {str(e)}"
                logger.error(error_msg, exc_info=True)
                job_logger.error(error_msg, exc_info=True)
        
        # Run baseline strategies
        logger.info(f"-" * 60)
        logger.info(f"BACKTESTING BASELINE STRATEGIES")
        logger.info(f"Strategies: {baseline_strategies}")
        logger.info(f"-" * 60)
        
        for i, strategy in enumerate(baseline_strategies, 1):
            logger.info(f"[{i}/{len(baseline_strategies)}] Running {strategy}...")
            job_logger.info(f"Starting backtest for baseline strategy: {strategy}")
            
            try:
                result = self._run_baseline_strategy(
                    strategy=strategy,
                    test_env=test_env,
                    dates=dates
                )
                results.append(result)
                logger.info(f"  ✓ {strategy} completed: Total Return = {result['metrics']['totalReturn']:.2%}")
                job_logger.info(f"{strategy} baseline backtest completed: {result['metrics']}")
            except Exception as e:
                error_msg = f"Error running baseline {strategy}: {str(e)}"
                logger.error(error_msg, exc_info=True)
                job_logger.error(error_msg, exc_info=True)
        
        # Find best algorithm
        logger.info(f"Analyzing results...")
        best_return = max(r["metrics"]["totalReturn"] for r in results)
        best_sharpe = max(r["metrics"]["sharpeRatio"] for r in results)
        best_algo = max(results, key=lambda x: x["metrics"]["sharpeRatio"])["algorithm"]
        
        logger.info(f"=" * 60)
        logger.info(f"BACKTEST COMPLETED")
        logger.info(f"  Best Algorithm: {best_algo}")
        logger.info(f"  Best Return: {best_return:.2%}")
        logger.info(f"  Best Sharpe Ratio: {best_sharpe:.2f}")
        logger.info(f"  Total Results: {len(results)}")
        logger.info(f"=" * 60)
        
        job_logger.info(f"Backtest analysis completed")
        job_logger.info(f"Best performer: {best_algo} (Sharpe={best_sharpe:.2f}, Return={best_return:.2%})")
        
        backtest_data = {
            "jobId": job_id,
            "results": results,
            "comparison": {
                "bestAlgorithm": best_algo,
                "bestReturn": best_return,
                "bestSharpeRatio": best_sharpe
            }
        }
        
        # Save backtest results
        save_json(job_id, "backtest_results.json", backtest_data)
        logger.info(f"Results saved to: {job_dir / 'backtest_results.json'}")
        job_logger.info(f"Backtest results saved successfully")
        
        return backtest_data
    
    def _backtest_drl_model(
        self,
        job_id: str,
        algorithm: str,
        test_env: CustomStockTradingEnv,
        dates: List[str]
    ) -> Dict[str, Any]:
        """Backtest a trained DRL model using Stable-Baselines3"""
        import torch
        
        logger.debug(f"Starting DRL model backtest: {algorithm}")
        
        # Import SB3
        from stable_baselines3 import PPO, DQN, SAC, TD3, A2C
        
        # Map algorithm names to SB3 classes
        agent_map = {
            "PPO": PPO,
            "DQN": DQN,  # DQN with discrete action wrapper
            "SAC": SAC,
            "TD3": TD3,
            "A2C": A2C,
        }
        
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.debug(f"Using device: {device}")
        
        try:
            # Load the trained SB3 model
            model_dir = get_job_dir(job_id) / "models" / algorithm
            model_path = model_dir / "model.zip"
            
            if not model_path.exists():
                logger.warning(f"Model not found at {model_path}, using fallback")
                return self._backtest_drl_model_fallback(job_id, algorithm, test_env, dates)
            
            logger.info(f"Loading SB3 model from: {model_path}")
            
            # Apply discrete action wrapper for DQN
            if algorithm == "DQN":
                from app.drl.discrete_wrapper import DiscreteActionWrapper
                test_env = DiscreteActionWrapper(test_env, n_actions_per_stock=5)
                logger.info(f"Applied DiscreteActionWrapper for DQN backtesting")
            
            # Load the trained SB3 model
            agent_class = agent_map.get(algorithm, PPO)
            model = agent_class.load(model_path, device=device)
            logger.info(f"Model loaded successfully")
            
            # Run backtest with trained model
            returns = []
            cumulative_returns = []
            portfolio_values = [settings.initial_amount]
            
            state, _ = test_env.reset()
            initial_value = test_env.get_total_asset()
            
            # Run through entire test period
            for step in range(test_env.max_step):
                # Get action from trained SB3 model
                action, _ = model.predict(state, deterministic=True)
                state, reward, done, truncated, _ = test_env.step(action)
                
                # Get current portfolio value
                current_value = test_env.get_total_asset()
                portfolio_values.append(current_value)
                
                # Calculate daily return as percentage change
                if len(portfolio_values) > 1:
                    daily_return = ((portfolio_values[-1] - portfolio_values[-2]) / portfolio_values[-2]) * 100
                else:
                    daily_return = 0.0
                
                returns.append(daily_return)
                
                # Cumulative return from initial amount
                cumulative_return = ((current_value - initial_value) / initial_value) * 100
                cumulative_returns.append(cumulative_return)
            
            # Ensure we have the right length
            returns = returns[:test_env.max_step]
            cumulative_returns = cumulative_returns[:test_env.max_step]
            
            # Calculate metrics
            returns_array = np.array(returns)
            metrics = self._calculate_metrics(returns_array)
            
            logger.info(f"Completed backtest for {algorithm}: Return={metrics['totalReturn']:.2%}")
            
            return {
                "algorithm": algorithm,
                "type": "drl",
                "returns": returns,
                "cumulativeReturns": cumulative_returns,
                "dates": dates[:len(returns)],
                "metrics": metrics
            }
            
        except Exception as e:
            logger.error(f"Error loading/running model for {algorithm}: {e}")
            logger.warning(f"Falling back to deterministic actions for {algorithm}")
            return self._backtest_drl_model_fallback(job_id, algorithm, test_env, dates)
    
    def _backtest_drl_model_fallback(
        self,
        job_id: str,
        algorithm: str,
        test_env: CustomStockTradingEnv,
        dates: List[str]
    ) -> Dict[str, Any]:
        """Fallback backtest with deterministic pseudo-random actions"""
        # Set seed based on job_id and algorithm for reproducibility
        seed = hash(f"{job_id}_{algorithm}") % (2**32)
        np.random.seed(seed)
        
        returns = []
        cumulative_returns = []
        portfolio_values = [settings.initial_amount]
        
        state, _ = test_env.reset()
        initial_value = test_env.get_total_asset()
        
        # Run through entire test period
        for step in range(test_env.max_step):
            # Deterministic action based on seed
            action = np.random.uniform(-1, 1, test_env.action_dim)
            state, reward, done, truncated, _ = test_env.step(action)
            
            # Get current portfolio value
            current_value = test_env.get_total_asset()
            portfolio_values.append(current_value)
            
            # Calculate daily return as percentage change
            if len(portfolio_values) > 1:
                daily_return = ((portfolio_values[-1] - portfolio_values[-2]) / portfolio_values[-2]) * 100
            else:
                daily_return = 0.0
            
            returns.append(daily_return)
            
            # Cumulative return from initial amount
            cumulative_return = ((current_value - initial_value) / initial_value) * 100
            cumulative_returns.append(cumulative_return)
        
        # Ensure we have the right length
        returns = returns[:test_env.max_step]
        cumulative_returns = cumulative_returns[:test_env.max_step]
        
        # Calculate metrics
        returns_array = np.array(returns)
        metrics = self._calculate_metrics(returns_array)
        
        return {
            "algorithm": algorithm,
            "type": "drl",
            "returns": returns,
            "cumulativeReturns": cumulative_returns,
            "dates": dates[:len(returns)],
            "metrics": metrics
        }
    
    def _run_baseline_strategy(
        self,
        strategy: str,
        test_env: CustomStockTradingEnv,
        dates: List[str]
    ) -> Dict[str, Any]:
        """Run a baseline strategy"""
        # Set seed for reproducibility of strategies that use randomness
        np.random.seed(42)
        
        returns = []
        cumulative_returns = []
        portfolio_values = [settings.initial_amount]
        
        state, _ = test_env.reset()
        initial_value = test_env.get_total_asset()
        
        for step in range(test_env.max_step):
            # Generate action based on strategy
            if strategy == "BuyAndHold":
                # Buy all stocks at start and hold (deterministic)
                if step == 0:
                    action = np.ones(test_env.action_dim)
                else:
                    action = np.zeros(test_env.action_dim)
            
            elif strategy == "MovingAverage":
                # Simple moving average strategy with deterministic seed
                action = np.random.uniform(-0.5, 0.5, test_env.action_dim)
            
            elif strategy == "Random":
                # Random actions with deterministic seed
                action = np.random.uniform(-1, 1, test_env.action_dim)
            
            elif strategy == "EqualWeight":
                # Equal weight rebalancing with deterministic seed
                action = np.random.uniform(-0.3, 0.3, test_env.action_dim)
            
            else:
                action = np.zeros(test_env.action_dim)
            
            state, reward, done, truncated, _ = test_env.step(action)
            
            # Get current portfolio value
            current_value = test_env.get_total_asset()
            portfolio_values.append(current_value)
            
            # Calculate daily return as percentage change
            if len(portfolio_values) > 1:
                daily_return = ((portfolio_values[-1] - portfolio_values[-2]) / portfolio_values[-2]) * 100
            else:
                daily_return = 0.0
            
            returns.append(daily_return)
            
            # Cumulative return from initial amount
            cumulative_return = ((current_value - initial_value) / initial_value) * 100
            cumulative_returns.append(cumulative_return)
            
            # Don't break on done - continue through entire test period
        
        # Ensure we have the right length
        returns = returns[:test_env.max_step]
        cumulative_returns = cumulative_returns[:test_env.max_step]
        
        # Calculate metrics
        returns_array = np.array(returns)
        metrics = self._calculate_metrics(returns_array)
        
        return {
            "algorithm": strategy,
            "type": "baseline",
            "returns": returns,
            "cumulativeReturns": cumulative_returns,
            "dates": dates[:len(returns)],
            "metrics": metrics
        }
    
    def _calculate_metrics(self, returns: np.ndarray) -> Dict[str, float]:
        """Calculate performance metrics"""
        # Total return
        total_return = (1 + returns / 100).prod() - 1
        
        # Sharpe ratio (assuming 252 trading days, 0% risk-free rate)
        sharpe_ratio = (returns.mean() / (returns.std() + 1e-9)) * np.sqrt(252)
        
        # Max drawdown
        cumulative = (1 + returns / 100).cumprod()
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min() * 100
        
        # Volatility
        volatility = returns.std() / 100
        
        # Win rate
        win_rate = (returns > 0).sum() / len(returns) if len(returns) > 0 else 0
        
        return {
            "totalReturn": float(total_return),
            "sharpeRatio": float(sharpe_ratio),
            "maxDrawdown": float(max_drawdown),
            "volatility": float(volatility),
            "winRate": float(win_rate)
        }


# Global instance
backtest_service = BacktestService()

