"""Stable-Baselines3 Training Wrapper"""
import os
import sys
import time
import torch as th
import numpy as np
from pathlib import Path
from typing import Dict, Any, Callable, Optional
import logging

# Import Stable-Baselines3
from stable_baselines3 import PPO, DQN, SAC, TD3, A2C
from stable_baselines3.common.callbacks import BaseCallback

# Import custom logger
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.logger import trainer_logger as logger


class ProgressCallback(BaseCallback):
    """Custom callback for progress tracking"""
    
    def __init__(self, callback_fn: Optional[Callable], total_timesteps: int, verbose: int = 0):
        """
        Args:
            callback_fn: Callback function(epoch, loss, reward, status)
            total_timesteps: Total training timesteps
            verbose: Verbosity level
        """
        super().__init__(verbose)
        self.callback_fn = callback_fn
        self.total_timesteps = total_timesteps
        self.episode_rewards = []
        self.episode_losses = []
        self.last_progress_update = 0
        self.update_interval = 100  # Update progress every 100 steps
        self.last_loss = 0.0  # Track last loss value
        self.last_reward = 0.0  # Track last reward value
        
    def _on_step(self) -> bool:
        """Called after each step"""
        # Update progress at intervals
        if self.num_timesteps - self.last_progress_update >= self.update_interval:
            self.last_progress_update = self.num_timesteps
            
            # Calculate progress (0-1000 scale)
            progress = int((self.num_timesteps / self.total_timesteps) * 1000)
            
            # Get episode reward from rollout buffer if available
            avg_reward = 0.0
            if hasattr(self.model, 'ep_info_buffer') and len(self.model.ep_info_buffer) > 0:
                avg_reward = np.mean([ep_info['r'] for ep_info in self.model.ep_info_buffer])
            
            # Get loss from logger if available
            # Different algorithms use different logger keys
            avg_loss = 0.0
            if hasattr(self.model, 'logger') and self.model.logger is not None:
                try:
                    if hasattr(self.model.logger, 'name_to_value'):
                        # Try algorithm-specific loss keys
                        # PPO/A2C: policy_loss, value_loss, loss
                        # DQN: loss
                        # SAC: actor_loss, critic_loss, ent_coef_loss  
                        # TD3: actor_loss, critic_loss
                        loss_keys = [
                            'train/loss',           # DQN, general
                            'train/policy_loss',    # PPO, A2C
                            'train/value_loss',     # PPO, A2C (critic)
                            'train/actor_loss',     # SAC, TD3
                            'train/critic_loss',    # SAC, TD3
                        ]
                        
                        # Get first available loss
                        for key in loss_keys:
                            if key in self.model.logger.name_to_value:
                                avg_loss = self.model.logger.name_to_value[key]
                                break
                except Exception as e:
                    logger.debug(f"Failed to get loss from logger: {e}")
            
            # Store last values for final reporting
            self.last_loss = float(avg_loss)
            self.last_reward = float(avg_reward)
            
            # Callback to update progress
            if self.callback_fn:
                self.callback_fn(
                    epoch=self.num_timesteps,
                    loss=self.last_loss,
                    reward=self.last_reward,
                    status="training"
                )
            
            # Log progress
            if self.verbose > 0:
                logger.debug(f"Progress: {self.num_timesteps}/{self.total_timesteps}, "
                           f"Reward: {avg_reward:.2f}, Loss: {avg_loss:.4f}")
        
        return True


class DRLTrainer:
    """Wrapper for Stable-Baselines3 training"""
    
    # Map algorithm names to SB3 classes
    AGENT_MAP = {
        "PPO": PPO,
        "DQN": DQN,  # DQN with discrete action wrapper
        "SAC": SAC,
        "TD3": TD3,
        "A2C": A2C,
    }
    
    def __init__(self, env, algorithm: str, model_dir: str, progress_callback: Callable = None):
        """
        Initialize trainer
        
        Args:
            env: Trading environment (Gym-compatible)
            algorithm: Algorithm name (PPO, DQN, SAC, TD3, A2C)
            model_dir: Directory to save model
            progress_callback: Callback function(epoch, loss, reward, status)
        """
        self.base_env = env  # Keep reference to base environment
        self.algorithm = algorithm
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.progress_callback = progress_callback
        
        if algorithm not in self.AGENT_MAP:
            raise ValueError(f"Unknown algorithm: {algorithm}. Available: {list(self.AGENT_MAP.keys())}")
        
        self.agent_class = self.AGENT_MAP[algorithm]
        self.model = None
        self.device = "cuda" if th.cuda.is_available() else "cpu"
        
        # Apply discrete action wrapper for DQN
        if algorithm == "DQN":
            from app.drl.discrete_wrapper import DiscreteActionWrapper
            self.env = DiscreteActionWrapper(env, n_actions_per_stock=3)
            logger.info(f"Applied DiscreteActionWrapper for DQN (3 actions per stock)")
        else:
            self.env = env
        
        logger.info(f"=" * 70)
        logger.info(f"INITIALIZING DRL TRAINER (Stable-Baselines3)")
        logger.info(f"Algorithm: {algorithm}")
        logger.info(f"Device: {self.device}")
        logger.info(f"Model Directory: {model_dir}")
        logger.info(f"Environment: state_dim={self.env.observation_space.shape}, "
                   f"action_dim={self.env.action_space.shape if hasattr(self.env.action_space, 'shape') else self.env.action_space.n}, "
                   f"max_step={self.base_env.max_step}")
        logger.info(f"=" * 70)
    
    def train(
        self,
        total_timesteps: int = 10000,
        learning_rate: float = 3e-4,
        batch_size: int = 256,
        verbose: int = 1
    ) -> Dict[str, Any]:
        """
        Train the agent using Stable-Baselines3
        
        Args:
            total_timesteps: Total training timesteps
            learning_rate: Learning rate
            batch_size: Batch size
            verbose: Verbosity level (0: no output, 1: info, 2: debug)
        
        Returns:
            Training metrics dictionary
        """
        logger.info(f"-" * 70)
        logger.info(f"STARTING TRAINING")
        logger.info(f"Algorithm: {self.algorithm}")
        logger.info(f"Total Timesteps: {total_timesteps}")
        logger.info(f"Learning Rate: {learning_rate}")
        logger.info(f"Batch Size: {batch_size}")
        logger.info(f"Device: {self.device}")
        logger.info(f"-" * 70)
        
        # Algorithm-specific hyperparameters
        kwargs = {
            "learning_rate": learning_rate,
            "device": self.device,
            "verbose": verbose,
            "seed": int(time.time() * 1000) % 10000
        }
        
        # Algorithm-specific settings (optimized based on ElegantRL best practices)
        # Reference: ElegantRL tutorials and examples
        max_step = self.base_env.max_step
        
        if self.algorithm == "PPO":
            # PPO: On-policy algorithm, requires multiple epochs per update
            # ElegantRL recommendation: n_steps=max_step*2-8, batch_size=256-512, n_epochs=10-16
            kwargs.update({
                "policy_kwargs": dict(net_arch=[256, 128]),  # Network architecture
                "n_steps": max(max_step * 2, 1024),  # Collect 2x episode length
                "batch_size": 256,  # Larger batch for stability
                "n_epochs": 16,  # More epochs for better convergence
                "gamma": 0.99,  # Discount factor
                "gae_lambda": 0.97,  # GAE lambda (higher for better advantage estimation)
                "clip_range": 0.2,  # PPO clip parameter
                "ent_coef": 0.02,  # Entropy coefficient (increased for exploration)
                "vf_coef": 0.5,  # Value function coefficient
                "max_grad_norm": 0.5,  # Gradient clipping
            })
            logger.info(f"PPO: n_steps={kwargs['n_steps']}, batch_size=256, n_epochs=16")
            
        elif self.algorithm == "A2C":
            # A2C: On-policy synchronous actor-critic
            # ElegantRL recommendation: n_steps=max_step*2-4, learning_rate=2e-4 to 4e-4
            kwargs.update({
                "policy_kwargs": dict(net_arch=[256, 128]),
                "n_steps": max(max_step * 2, 512),  # Collect 2x episode length
                "gamma": 0.99,
                "gae_lambda": 0.97,  # Increased from 1.0 for better variance reduction
                "ent_coef": 0.02,  # Increased from 0.0 for exploration
                "vf_coef": 0.5,  # Value function coefficient
                "max_grad_norm": 0.5,  # Gradient clipping
                "normalize_advantage": True,  # Normalize advantages
                "use_rms_prop": True,  # Use RMSProp optimizer (standard for A2C)
            })
            # Override learning rate for A2C (higher than default)
            kwargs["learning_rate"] = 3e-4
            logger.info(f"A2C: n_steps={kwargs['n_steps']}, learning_rate=3e-4, normalize_advantage=True")
            
        elif self.algorithm == "DQN":
            # DQN: Off-policy value-based algorithm with discrete actions
            # ElegantRL recommendation: buffer_size=50k-100k, batch_size=64-128, learning_starts=1000
            kwargs.update({
                "policy_kwargs": dict(net_arch=[128, 64]),
                "buffer_size": 100000,  # Large replay buffer
                "learning_starts": max(1000, max_step * 2),  # Start learning after sufficient exploration
                "batch_size": 128,  # Moderate batch size
                "tau": 1.0,  # Hard target network update
                "gamma": 0.99,
                "train_freq": 1,  # Update every step
                "gradient_steps": 1,
                "target_update_interval": 500,  # Update target network every 500 steps (increased from 1000)
                "exploration_fraction": 0.2,  # 20% of training for exploration (increased from 0.1)
                "exploration_initial_eps": 1.0,
                "exploration_final_eps": 0.05,
            })
            logger.info(f"DQN: buffer_size=100k, learning_starts={kwargs['learning_starts']}, exploration_fraction=0.2")
            
        elif self.algorithm == "SAC":
            # SAC: Off-policy entropy-regularized actor-critic
            # ElegantRL recommendation: net_arch=[256,256], batch_size=256-1024, buffer_size=100k-1M
            # SAC performs well with large buffers and batch sizes
            kwargs.update({
                "policy_kwargs": dict(net_arch=[256, 256]),  # Larger network for SAC
                "buffer_size": 200000,  # Large buffer (increased from 50k)
                "learning_starts": max(2000, max_step * 3),  # More initial exploration (increased from 200)
                "batch_size": 512,  # Larger batch size (increased from 128)
                "tau": 0.005,  # Soft update coefficient
                "gamma": 0.99,
                "train_freq": 1,
                "gradient_steps": 1,
                "ent_coef": "auto",  # Auto-tune entropy coefficient
                "target_entropy": "auto",
            })
            logger.info(f"SAC: buffer_size=200k, batch_size=512, learning_starts={kwargs['learning_starts']}")
            
        elif self.algorithm == "TD3":
            # TD3: Off-policy twin delayed DDPG
            # ElegantRL recommendation: net_arch=[256,128], batch_size=256-512, policy_noise=0.1-0.2
            kwargs.update({
                "policy_kwargs": dict(net_arch=[256, 128]),
                "buffer_size": 200000,  # Large buffer (increased from 50k)
                "learning_starts": max(2000, max_step * 3),  # More initial exploration (increased from 200)
                "batch_size": 512,  # Larger batch size (increased from 128)
                "tau": 0.005,  # Soft update coefficient
                "gamma": 0.99,
                "train_freq": 1,
                "gradient_steps": 1,
                "policy_delay": 2,  # Update policy every 2 critic updates
                "target_policy_noise": 0.2,  # Noise for target policy smoothing
                "target_noise_clip": 0.5,  # Clip target noise
            })
            logger.info(f"TD3: buffer_size=200k, batch_size=512, learning_starts={kwargs['learning_starts']}")
        
        logger.info(f"Algorithm-specific hyperparameters: {kwargs}")
        
        # Create model
        try:
            logger.info(f"Creating {self.algorithm} model with MlpPolicy...")
            self.model = self.agent_class(
                "MlpPolicy",
                self.env,
                **kwargs
            )
            logger.info(f"Model created successfully")
        except Exception as e:
            logger.error(f"Failed to create model: {e}", exc_info=True)
            raise
        
        # Create progress callback
        callback = ProgressCallback(
            callback_fn=self.progress_callback,
            total_timesteps=total_timesteps,
            verbose=verbose
        )
        
        # Train
        start_time = time.time()
        try:
            logger.info(f"Starting training loop...")
            self.model.learn(
                total_timesteps=total_timesteps,
                callback=callback,
                progress_bar=False  # We use our own progress tracking
            )
            training_time = time.time() - start_time
            logger.info(f"Training completed successfully in {training_time:.1f}s")
        except Exception as e:
            logger.error(f"Training failed: {e}", exc_info=True)
            raise
        
        # Evaluate final performance
        logger.info(f"Evaluating final model performance...")
        eval_start = time.time()
        final_reward, final_std = self._evaluate(num_episodes=5)
        eval_time = time.time() - eval_start
        
        logger.info(f"=" * 70)
        logger.info(f"TRAINING COMPLETED")
        logger.info(f"  Algorithm: {self.algorithm}")
        logger.info(f"  Total Timesteps: {total_timesteps}")
        logger.info(f"  Training Time: {training_time:.1f}s")
        logger.info(f"  Final Reward: {final_reward:.2f} ± {final_std:.2f}")
        logger.info(f"  Evaluation Time: {eval_time:.1f}s")
        logger.info(f"=" * 70)
        
        # Save model
        model_path = self.model_dir / "model"
        try:
            self.model.save(model_path)
            logger.info(f"Model saved to: {model_path}.zip")
        except Exception as e:
            logger.error(f"Failed to save model: {e}", exc_info=True)
            raise
        
        # Get final loss from callback
        final_loss = callback.last_loss if hasattr(callback, 'last_loss') else 0.0
        
        # Return metrics
        results = {
            "total_steps": total_timesteps,
            "training_time": training_time,
            "final_reward": float(final_reward),
            "final_std": float(final_std),
            "final_loss": float(final_loss),  # Include loss in results
            "best_reward": float(final_reward),  # SB3 doesn't track best separately during training
        }
        logger.debug(f"Training results: {results}")
        logger.info(f"Final loss from training: {final_loss:.4f}")
        
        return results
    
    def _evaluate(self, num_episodes: int = 5) -> tuple:
        """
        Evaluate the trained model
        
        Args:
            num_episodes: Number of evaluation episodes
        
        Returns:
            (mean_reward, std_reward)
        """
        if self.model is None:
            logger.warning("No model to evaluate")
            return 0.0, 0.0
        
        logger.debug(f"Evaluating for {num_episodes} episodes...")
        rewards = []
        
        for i in range(num_episodes):
            state, _ = self.env.reset()
            episode_reward = 0.0
            done = False
            step = 0
            
            while not done and step < self.env.max_step:
                # Use deterministic actions for evaluation
                action, _ = self.model.predict(state, deterministic=True)
                state, reward, terminated, truncated, info = self.env.step(action)
                episode_reward += reward
                done = terminated or truncated
                step += 1
            
            # Get final portfolio value for calculating return
            # Use environment's total_asset / initial_amount as the true return
            env_unwrapped = getattr(self.env, 'unwrapped', self.env)
            if hasattr(env_unwrapped, 'get_total_asset') and hasattr(env_unwrapped, 'initial_amount'):
                # Calculate return rate from final portfolio value
                final_value = env_unwrapped.get_total_asset()
                return_rate = (final_value - env_unwrapped.initial_amount) / env_unwrapped.initial_amount
                episode_reward = return_rate
                logger.debug(f"  Episode {i+1}: portfolio ${final_value:.2f}, return {return_rate:.4f}")
            
            rewards.append(episode_reward)
            logger.debug(f"  Episode {i+1}/{num_episodes}: reward={episode_reward:.4f}")
        
        mean_reward = np.mean(rewards)
        std_reward = np.std(rewards)
        logger.debug(f"Evaluation complete: {mean_reward:.2f} ± {std_reward:.2f}")
        
        return mean_reward, std_reward
    
    def get_model_path(self) -> str:
        """Get path to the trained model"""
        model_path = self.model_dir / "model.zip"
        return str(model_path)
    
    def load_model(self, model_path: Optional[str] = None):
        """Load a trained model"""
        if model_path is None:
            model_path = self.get_model_path()
        
        try:
            logger.info(f"Loading model from: {model_path}")
            self.model = self.agent_class.load(model_path, device=self.device)
            logger.info(f"Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}", exc_info=True)
            raise
