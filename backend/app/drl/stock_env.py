"""Custom Stock Trading Environment for DRL"""
import numpy as np
from typing import Tuple, Optional
import logging
import gymnasium as gym
from gymnasium import spaces

logger = logging.getLogger(__name__)

ARY = np.ndarray


class CustomStockTradingEnv(gym.Env):
    """
    Custom Stock Trading Environment that uses database data
    
    State space: [cash, shares_per_stock, close_prices, technical_indicators]
    Action space: continuous action per stock (buy/sell amount)
    """
    
    def __init__(
        self,
        close_ary: ARY,
        tech_ary: ARY,
        initial_amount: float = 1e6,
        max_stock: int = 100,
        cost_pct: float = 0.001,
        gamma: float = 0.99,
        beg_idx: int = 0,
        end_idx: Optional[int] = None
    ):
        """
        Initialize trading environment
        
        Args:
            close_ary: Shape (days, num_stocks) - closing prices
            tech_ary: Shape (days, num_features) - technical indicators
            initial_amount: Initial cash amount
            max_stock: Maximum shares to trade per action
            cost_pct: Transaction cost percentage
            gamma: Discount factor for rewards
            beg_idx: Beginning index in data
            end_idx: Ending index in data (None for all data)
        """
        super().__init__()
        
        # Data slicing
        if end_idx is None:
            end_idx = len(close_ary)
        
        self.close_ary = close_ary[beg_idx:end_idx]
        self.tech_ary = tech_ary[beg_idx:end_idx]
        
        logger.info(f"Environment initialized with close_ary shape: {self.close_ary.shape}")
        logger.info(f"Environment initialized with tech_ary shape: {self.tech_ary.shape}")
        
        # Trading parameters
        self.initial_amount = initial_amount
        self.max_stock = max_stock
        self.cost_pct = cost_pct
        self.gamma = gamma
        # 增大reward_scale以提供更明显的奖励信号
        # 从2^-12 (0.000244) 提高到2^-8 (0.00391)
        self.reward_scale = 2 ** -8  # 修改为更大的奖励缩放
        
        # Environment state
        self.day = None
        self.rewards = None
        self.total_asset = None
        self.cumulative_returns = 0
        self.if_random_reset = False  # Deterministic reset for stability
        
        self.amount = None
        self.shares = None
        self.shares_num = self.close_ary.shape[1]
        
        # Environment information
        self.env_name = 'CustomStockTradingEnv'
        # Improved state space: 资金状态(2维) + 每只股票(4维)
        # - 资金状态: 现金比例, 总资产收益率
        # - 每只股票: 仓位占比, 日收益率, 归一化RSI, 归一化MACD
        self.state_dim = 2 + self.shares_num * 4
        self.action_dim = self.shares_num
        self.if_discrete = False
        self.max_step = self.close_ary.shape[0] - 1
        self.target_return = +np.inf
        
        # Gymnasium spaces (required by Stable-Baselines3)
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(self.state_dim,),
            dtype=np.float32
        )
        self.action_space = spaces.Box(
            low=-1.0,
            high=1.0,
            shape=(self.action_dim,),
            dtype=np.float32
        )
        
        logger.info(f"State dim: {self.state_dim}, Action dim: {self.action_dim}")
        logger.info(f"Max steps: {self.max_step}")
    
    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None) -> Tuple[ARY, dict]:
        """Reset environment to initial state"""
        if seed is not None:
            np.random.seed(seed)
        
        self.day = 0
        
        if self.if_random_reset:
            self.amount = self.initial_amount * np.random.uniform(0.9, 1.1)
            self.shares = (
                np.abs(np.random.randn(self.shares_num).clip(-2, +2)) * 2 ** 6
            ).astype(int)
        else:
            self.amount = self.initial_amount
            self.shares = np.zeros(self.shares_num, dtype=np.float32)
        
        self.rewards = []
        self.total_asset = (self.close_ary[self.day] * self.shares).sum() + self.amount
        self.prev_prices = self.close_ary[0].copy()  # Initialize previous prices
        
        return self.get_state(), {}
    
    def get_state(self) -> ARY:
        """
        Get improved state representation
        
        State composition:
        1. Financial state (2 dims): cash ratio, portfolio return
        2. Per stock (4 dims): position ratio, daily return, normalized RSI, normalized MACD
        """
        day_idx = min(self.day, len(self.close_ary) - 1)
        current_prices = self.close_ary[day_idx]
        
        # 1. Financial state (2 dims)
        cash_ratio = self.amount / self.total_asset if self.total_asset > 0 else 0
        portfolio_return = (self.total_asset - self.initial_amount) / self.initial_amount
        
        state_parts = [
            np.tanh(cash_ratio - 0.5),   # Cash ratio (normalized)
            np.tanh(portfolio_return)     # Total return
        ]
        
        # 2. Per stock state (4 dims each)
        stock_values = current_prices * self.shares
        for i in range(self.shares_num):
            # Position ratio (stock value / total asset)
            position_ratio = stock_values[i] / self.total_asset if self.total_asset > 0 else 0
            
            # Daily return
            daily_return = (current_prices[i] - self.prev_prices[i]) / self.prev_prices[i] \
                          if self.prev_prices[i] > 0 else 0
            
            # Normalized technical indicators
            tech_idx = i * 8  # 8 indicators per stock
            # RSI (indicator 3)
            rsi_raw = self.tech_ary[day_idx, tech_idx + 3] if tech_idx + 3 < self.tech_ary.shape[1] else 50
            rsi_norm = np.tanh((rsi_raw - 50) / 50)
            
            # MACD (indicator 0)
            macd_raw = self.tech_ary[day_idx, tech_idx] if tech_idx < self.tech_ary.shape[1] else 0
            macd_norm = np.tanh(macd_raw / (current_prices[i] + 1e-8))
            
            state_parts.extend([
                np.tanh(position_ratio),
                np.tanh(daily_return * 10),  # Amplify signal
                rsi_norm,
                macd_norm
            ])
        
        return np.array(state_parts, dtype=np.float32)
    
    def step(self, action: ARY) -> Tuple[ARY, float, bool, bool, dict]:
        """
        Improved trading execution logic
        
        Args:
            action: Target position ratios (per stock), will be normalized via softmax
        
        Returns:
            state: Next state
            reward: Reward for this step
            terminal: Whether episode is done
            truncated: Whether episode was truncated
            info: Additional information
        """
        self.day += 1
        
        # Check if we've reached the end of data BEFORE processing
        if self.day >= len(self.close_ary):
            # Episode is done, return final state
            terminal = True
            state = self.get_state() if self.day > 0 else np.zeros(self.state_dim, dtype=np.float32)
            reward = 0.0
            if self.rewards:
                reward = 1 / (1 - self.gamma) * np.mean(self.rewards)
            return state, reward, terminal, False, {}
        
        # Update previous prices
        if self.day > 0:
            self.prev_prices = self.close_ary[self.day - 1].copy()
        
        # === New action processing: Target position ratios ===
        current_prices = self.close_ary[self.day]
        
        # 1. Softmax normalization to get target weights
        exp_action = np.exp(action - np.max(action))  # Numerical stability
        target_weights = exp_action / exp_action.sum()
        
        # 2. Calculate target position values
        investable_amount = self.total_asset * 0.95  # Reserve 5% cash buffer
        target_values = investable_amount * target_weights
        
        # 3. Calculate current position values
        current_values = current_prices * self.shares
        
        # 4. Execute trades to reach target positions
        for i in range(self.action_dim):
            value_diff = target_values[i] - current_values[i]
            price = current_prices[i]
            
            if value_diff > 0:  # Need to buy
                # Calculate max buyable amount
                max_buy_value = min(self.amount * 0.99, value_diff)  # Leave 1% buffer
                shares_to_buy = int(max_buy_value / (price * (1 + self.cost_pct)))
                
                if shares_to_buy > 0:
                    cost = price * shares_to_buy * (1 + self.cost_pct)
                    self.amount -= cost
                    self.shares[i] += shares_to_buy
                    
            elif value_diff < 0 and self.shares[i] > 0:  # Need to sell
                shares_to_sell = int(min(abs(value_diff) / price, self.shares[i]))
                
                if shares_to_sell > 0:
                    proceeds = price * shares_to_sell * (1 - self.cost_pct)
                    self.amount += proceeds
                    self.shares[i] -= shares_to_sell
        
        # Calculate reward
        total_asset = (current_prices * self.shares).sum() + self.amount
        reward = (total_asset - self.total_asset) * self.reward_scale
        self.rewards.append(reward)
        self.total_asset = total_asset
        
        # Check if episode is done
        terminal = self.day >= self.max_step
        if terminal:
            # Add terminal reward
            reward += 1 / (1 - self.gamma) * np.mean(self.rewards)
            self.cumulative_returns = total_asset / self.initial_amount
        
        state = self.get_state()
        truncated = False
        
        return state, reward, terminal, truncated, {}
    
    def get_total_asset(self) -> float:
        """Get current total asset value"""
        # Ensure day index is within bounds
        day_idx = min(self.day, len(self.close_ary) - 1)
        return (self.close_ary[day_idx] * self.shares).sum() + self.amount

