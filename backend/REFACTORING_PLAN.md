# DRL训练重构计划

## 🔍 问题根源

经过深入分析和多次测试，问题在于：

1. **ElegantRL的设计**:
   - 环境返回numpy arrays ✅ (符合Gym标准)
   - Agent内部方法期望torch tensors ❌ (实现细节)
   - `agent.explore_action(state)` 需要tensor输入
   - `agent.act.get_action(state)` 需要tensor输入

2. **转换点缺失**:
   - `AgentBase._explore_one_env()` 直接使用环境返回的state
   - 没有自动将numpy转为tensor
   - ElegantRL可能假设使用VectorizedEnv或特定的环境wrapper

## 🎯 解决方案

### 方案1: Monkey Patch Agent方法 (推荐)
在创建agent后，包装其所有与环境交互的方法：

```python
# 包装explore_action
原本: action = agent.explore_action(numpy_state)  # 失败
修改: action = agent.explore_action(tensor_state)  # 我们处理转换
```

### 方案2: 修改环境返回tensor
让环境直接返回tensor而不是numpy，但这违反Gym标准。

### 方案3: 完全重写训练循环 
不使用agent.explore_env()，自己写探索逻辑，完全控制转换。

### 方案4: 使用Stable-Baselines3
换用更成熟、文档更完善的DRL库。

## 📝 实施计划

采用方案1，在trainer.py中：

1. 创建agent后，保存原始方法
2. 创建wrapper函数处理numpy→tensor转换
3. 替换agent的方法为wrapper版本
4. 确保所有与环境交互的方法都被包装

关键方法：
- `explore_action(state)` - 需要tensor
- `select_actions(state)` - 需要tensor  
- `act.get_action(state)` - 需要tensor
- `act.state_norm(state)` - 需要tensor (PPO)

## ⚠️ 风险

- Monkey patching可能导致难以调试的bug
- ElegantRL更新可能破坏兼容性
- 性能开销（numpy↔tensor转换）

## 💡 长期解决方案

考虑迁移到Stable-Baselines3:
- 更好的文档和社区支持
- 更成熟的实现
- 原生支持Gym环境
- 更简单的API


