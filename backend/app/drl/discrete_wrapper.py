"""Discrete Action Wrapper for DQN compatibility"""
import numpy as np
import gymnasium as gym
from gymnasium import spaces
from typing import Tuple, Any


class DiscreteActionWrapper(gym.Wrapper):
    """
    Wrapper to convert continuous action space to discrete for DQN.
    
    Maps discrete actions to continuous actions:
    - For single stock environment:
      0: Strong Sell (-1.0)
      1: Sell (-0.5)
      2: Hold (0.0)
      3: Buy (0.5)
      4: Strong Buy (1.0)
    """
    
    def __init__(self, env, n_actions_per_stock: int = 3):
        """
        Args:
            env: Base environment with continuous action space
            n_actions_per_stock: Number of discrete actions per stock (default: 3)
        """
        super().__init__(env)
        
        self.n_actions_per_stock = n_actions_per_stock
        self.n_stocks = env.action_dim
        
        # For DQN, we need a single Discrete space, not MultiDiscrete
        # Total actions = n_actions_per_stock ^ n_stocks
        total_actions = n_actions_per_stock ** self.n_stocks
        self.action_space = spaces.Discrete(total_actions)
        
        # Observation space remains the same
        self.observation_space = env.observation_space
        
        # Create action mapping
        self._create_action_mapping()
        
        # Pre-compute all action combinations for multi-stock
        self._create_action_combinations()
    
    def _create_action_mapping(self):
        """Create mapping from discrete actions to continuous values"""
        # Map discrete actions to continuous values in [-1, 1]
        if self.n_actions_per_stock == 3:
            # Simple: Sell, Hold, Buy
            self.discrete_to_continuous = np.array([-1.0, 0.0, 1.0])
        elif self.n_actions_per_stock == 5:
            # More granular: Strong Sell, Sell, Hold, Buy, Strong Buy
            self.discrete_to_continuous = np.array([-1.0, -0.5, 0.0, 0.5, 1.0])
        elif self.n_actions_per_stock == 7:
            # Very granular
            self.discrete_to_continuous = np.array([-1.0, -0.67, -0.33, 0.0, 0.33, 0.67, 1.0])
        else:
            # Generic linear mapping
            self.discrete_to_continuous = np.linspace(-1.0, 1.0, self.n_actions_per_stock)
    
    def _create_action_combinations(self):
        """Pre-compute all action combinations for multi-stock scenarios"""
        # For multi-stock, we need to map a single discrete action to 
        # a combination of actions for each stock
        # e.g., for 2 stocks with 5 actions each: action 0 = [0,0], action 1 = [0,1], ..., action 24 = [4,4]
        
        total_actions = self.n_actions_per_stock ** self.n_stocks
        self.action_to_stock_actions = np.zeros((total_actions, self.n_stocks), dtype=np.int32)
        
        for action_idx in range(total_actions):
            # Convert single action to multi-stock actions using base conversion
            temp = action_idx
            for stock_idx in range(self.n_stocks):
                self.action_to_stock_actions[action_idx, stock_idx] = temp % self.n_actions_per_stock
                temp //= self.n_actions_per_stock
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, dict]:
        """
        Convert discrete action to continuous and step the environment
        
        Args:
            action: Single discrete action (int)
        
        Returns:
            observation, reward, terminated, truncated, info
        """
        # Convert single discrete action to multi-stock discrete actions
        stock_actions = self.action_to_stock_actions[action]
        
        # Convert discrete actions to continuous
        continuous_action = np.array([
            self.discrete_to_continuous[stock_action] 
            for stock_action in stock_actions
        ])
        
        # Step the base environment with continuous action
        return self.env.step(continuous_action)
    
    def reset(self, **kwargs):
        """Reset the environment"""
        return self.env.reset(**kwargs)

