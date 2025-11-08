"""
快速修复方案 - 改进状态空间和归一化
在不大幅重构的前提下提升性能
"""

import numpy as np
from typing import Optional, Tuple
import gymnasium as gym
from gymnasium import spaces

ARY = np.ndarray


class ImprovedStockTradingEnv(gym.Env):
    """
    改进的多股票交易环境
    
    主要改进:
    1. 添加相对价格变化（收益率）
    2. 添加持仓比例信息
    3. 改进技术指标归一化
    4. 添加资金使用率
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
        super().__init__()
        
        # Data slicing
        if end_idx is None:
            end_idx = len(close_ary)
        
        self.close_ary = close_ary[beg_idx:end_idx]
        self.tech_ary = tech_ary[beg_idx:end_idx]
        
        # Trading parameters
        self.initial_amount = initial_amount
        self.max_stock = max_stock
        self.cost_pct = cost_pct
        self.gamma = gamma
        self.reward_scale = 2 ** -8
        
        # Environment state
        self.day = None
        self.rewards = None
        self.total_asset = None
        self.amount = None
        self.shares = None
        self.shares_num = self.close_ary.shape[1]
        
        # Previous prices for calculating returns
        self.prev_prices = None
        
        # Environment information
        self.env_name = 'ImprovedStockTradingEnv'
        
        # State dimension calculation
        # 改进后的状态空间：
        # - 资金状态: 2维 (现金比例, 总资产收益率)
        # - 每只股票: 6维 (持仓比例, 仓位占比, 日收益率, 周收益率, 归一化RSI, 归一化MACD)
        self.state_dim = 2 + self.shares_num * 6
        self.action_dim = self.shares_num
        self.if_discrete = False
        self.max_step = self.close_ary.shape[0] - 1
        
        # Gymnasium spaces
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
    
    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None) -> Tuple[ARY, dict]:
        """Reset environment"""
        if seed is not None:
            np.random.seed(seed)
        
        self.day = 0
        self.amount = self.initial_amount
        self.shares = np.zeros(self.shares_num, dtype=np.float32)
        self.rewards = []
        self.total_asset = self.initial_amount
        self.prev_prices = self.close_ary[0].copy()
        
        return self.get_state(), {}
    
    def get_state(self) -> ARY:
        """
        获取改进的状态表示
        
        状态组成:
        1. 资金状态 (2维):
           - 现金比例 (tanh标准化)
           - 总资产收益率 (tanh标准化)
        
        2. 每只股票 (6维):
           - 持仓比例 (该股票持仓数/总持仓数)
           - 仓位占比 (该股票市值/总资产)
           - 日收益率 (相对前一天)
           - 周收益率 (相对5天前)
           - 归一化技术指标1 (如RSI)
           - 归一化技术指标2 (如MACD)
        """
        day_idx = min(self.day, len(self.close_ary) - 1)
        
        # === 1. 资金状态 ===
        cash_ratio = self.amount / self.total_asset if self.total_asset > 0 else 0
        portfolio_return = (self.total_asset - self.initial_amount) / self.initial_amount
        
        state_financial = [
            np.tanh(cash_ratio - 0.5),  # 标准化到[-1,1]，0.5为中性
            np.tanh(portfolio_return)   # 总收益率
        ]
        
        # === 2. 每只股票的状态 ===
        current_prices = self.close_ary[day_idx]
        stock_values = current_prices * self.shares
        total_stock_value = stock_values.sum()
        total_shares = self.shares.sum()
        
        state_stocks = []
        for i in range(self.shares_num):
            # --- 持仓信息 ---
            # 持仓比例（该股票持仓/总持仓）
            share_ratio = self.shares[i] / total_shares if total_shares > 0 else 0
            # 仓位占比（该股票市值/总资产）
            position_ratio = stock_values[i] / self.total_asset if self.total_asset > 0 else 0
            
            # --- 价格变化信息 ---
            # 日收益率
            daily_return = (current_prices[i] - self.prev_prices[i]) / self.prev_prices[i] \
                          if self.prev_prices[i] > 0 else 0
            
            # 周收益率（5日）
            lookback = min(5, day_idx)
            if lookback > 0:
                past_price = self.close_ary[day_idx - lookback, i]
                weekly_return = (current_prices[i] - past_price) / past_price if past_price > 0 else 0
            else:
                weekly_return = 0
            
            # --- 技术指标（归一化）---
            # 假设tech_ary中每只股票有8个指标
            # 这里我们提取前2个并归一化
            tech_idx_start = i * 8  # 每只股票8个技术指标
            
            # 技术指标1：假设是RSI (0-100) → 归一化到[-1,1]
            tech1_raw = self.tech_ary[day_idx, tech_idx_start + 3] if tech_idx_start + 3 < self.tech_ary.shape[1] else 50
            tech1_norm = np.tanh((tech1_raw - 50) / 50)  # RSI中性值50
            
            # 技术指标2：假设是MACD → 归一化
            tech2_raw = self.tech_ary[day_idx, tech_idx_start + 0] if tech_idx_start < self.tech_ary.shape[1] else 0
            tech2_norm = np.tanh(tech2_raw / (current_prices[i] + 1e-8))  # 相对价格归一化
            
            # 组合该股票的所有特征
            stock_state = [
                np.tanh(share_ratio),
                np.tanh(position_ratio),
                np.tanh(daily_return * 10),   # 放大10倍增强信号
                np.tanh(weekly_return * 5),   # 放大5倍
                tech1_norm,
                tech2_norm
            ]
            state_stocks.extend(stock_state)
        
        # 合并所有状态
        state = np.array(state_financial + state_stocks, dtype=np.float32)
        
        # 确保状态维度正确
        assert len(state) == self.state_dim, f"State dim mismatch: {len(state)} vs {self.state_dim}"
        
        return state
    
    def step(self, action: ARY) -> Tuple[ARY, float, bool, bool, dict]:
        """执行交易步骤（保持原逻辑）"""
        self.day += 1
        
        if self.day >= len(self.close_ary):
            terminal = True
            state = self.get_state() if self.day > 0 else np.zeros(self.state_dim, dtype=np.float32)
            reward = 0.0
            if self.rewards:
                reward = 1 / (1 - self.gamma) * np.mean(self.rewards)
            return state, reward, terminal, False, {}
        
        # 保存当前价格作为下一步的"前一价格"
        self.prev_prices = self.close_ary[self.day - 1].copy() if self.day > 0 else self.close_ary[0].copy()
        
        # 处理动作（保持原有逻辑）
        action = action.copy()
        action[(-0.1 < action) & (action < 0.1)] = 0
        action_int = (action * self.max_stock).astype(int)
        
        # 执行交易
        for index in range(self.action_dim):
            stock_action = action_int[index]
            adj_close_price = self.close_ary[self.day, index]
            
            if stock_action > 0:  # Buy
                delta_stock = min(self.amount // adj_close_price, stock_action)
                self.amount -= adj_close_price * delta_stock * (1 + self.cost_pct)
                self.shares[index] += delta_stock
            elif self.shares[index] > 0:  # Sell
                delta_stock = min(-stock_action, self.shares[index])
                self.amount += adj_close_price * delta_stock * (1 - self.cost_pct)
                self.shares[index] -= delta_stock
        
        # 计算奖励
        total_asset = (self.close_ary[self.day] * self.shares).sum() + self.amount
        reward = (total_asset - self.total_asset) * self.reward_scale
        self.rewards.append(reward)
        self.total_asset = total_asset
        
        # 检查是否结束
        terminal = self.day >= self.max_step
        if terminal:
            reward += 1 / (1 - self.gamma) * np.mean(self.rewards)
        
        state = self.get_state()
        truncated = False
        
        return state, reward, terminal, truncated, {}
    
    def get_total_asset(self) -> float:
        """获取总资产"""
        day_idx = min(self.day, len(self.close_ary) - 1)
        return (self.close_ary[day_idx] * self.shares).sum() + self.amount


# ============================================
# 使用示例
# ============================================

if __name__ == "__main__":
    # 创建虚拟数据测试
    days = 100
    stocks = 3
    
    close_ary = np.random.randn(days, stocks).cumsum(axis=0) + 100
    close_ary = np.abs(close_ary)  # 确保价格为正
    
    tech_ary = np.random.randn(days, stocks * 8) * 10 + 50  # 8个技术指标/股票
    
    # 创建环境
    env = ImprovedStockTradingEnv(close_ary, tech_ary)
    
    # 测试重置
    state, info = env.reset(seed=42)
    print(f"Initial state shape: {state.shape}")
    print(f"State dim: {env.state_dim}")
    print(f"First few state values: {state[:10]}")
    
    # 测试步骤
    for i in range(10):
        action = np.random.randn(stocks) * 0.5  # 随机动作
        state, reward, done, truncated, info = env.step(action)
        print(f"Step {i+1}: reward={reward:.4f}, total_asset=${env.total_asset:.2f}")
        
        if done:
            break
    
    print("\n✓ 环境测试通过")
    print(f"最终状态维度: {state.shape}")
    print(f"最终资产: ${env.total_asset:.2f}")
    print(f"收益率: {(env.total_asset - env.initial_amount) / env.initial_amount * 100:.2f}%")

