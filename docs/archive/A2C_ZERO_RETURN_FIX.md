# A2C零收益Bug修复

## 问题
**Job ID**: `13a93121-819b-4c38-a33a-cad5fa30cd69`  
**算法**: A2C  
**现象**: 训练过程reward正常增长，但测试集评估返回0.0，最终returnRate=0.0%

## 根本原因

### Bug 1: `trainer.py` - `_evaluate`方法
```python
# 第396-397行（旧代码）
if hasattr(env_unwrapped, 'cumulative_returns'):
    episode_reward = env_unwrapped.cumulative_returns  # ❌ 覆盖累积reward
```

**问题**: `cumulative_returns`只在episode结束（terminal=True）时更新，如果episode未正常完成，值保持为0或1.0。

### Bug 2: `training_service.py` - `_evaluate_on_test`方法
```python
# 第304-306行（旧代码）
cumulative_return = getattr(env_unwrapped, 'cumulative_returns', 1.0)
returns.append(cumulative_return - 1.0)  # ❌ 1.0 - 1.0 = 0.0
```

**问题**: 同样依赖`cumulative_returns`，导致测试评估返回0。

## 修复方案

### 修复1: `trainer.py`
使用`get_total_asset()`直接计算最终收益率：
```python
if hasattr(env_unwrapped, 'get_total_asset') and hasattr(env_unwrapped, 'initial_amount'):
    final_value = env_unwrapped.get_total_asset()
    return_rate = (final_value - env_unwrapped.initial_amount) / env_unwrapped.initial_amount
    episode_reward = return_rate
```

### 修复2: `training_service.py`
同样使用`get_total_asset()`：
```python
if hasattr(env_unwrapped, 'get_total_asset') and hasattr(env_unwrapped, 'initial_amount'):
    final_value = env_unwrapped.get_total_asset()
    return_rate = (final_value - env_unwrapped.initial_amount) / env_unwrapped.initial_amount
    returns.append(return_rate)
```

## 影响范围
- ✅ **所有算法**（PPO, DQN, A2C, SAC, TD3）都受益于此修复
- ✅ 更准确的评估指标
- ✅ 避免对`cumulative_returns`更新时机的依赖

## 测试建议
重新训练A2C算法，验证：
1. 测试集reward不再为0
2. returnRate正常显示
3. Loss显示正常（已修复SAC/TD3 loss显示）

