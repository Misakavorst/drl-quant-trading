# Loss显示和A2C零收益问题修复

## 修复内容

### 1. SAC/TD3 Loss不显示 ✅
**原因**: logger key不匹配  
**修复**: 添加`train/actor_loss`和`train/critic_loss`到loss获取列表

### 2. A2C零收益Bug ✅ (关键修复)
**原因**: 评估方法依赖`cumulative_returns`，但该值只在episode结束时更新  
**修复**: 改用`get_total_asset()`直接计算最终收益率  
**详见**: `A2C_ZERO_RETURN_FIX.md`

### 2. Loss差异大的原因说明

**不同算法的Loss度量标准不同，不可直接比较**：

| 算法 | Loss含义 | 典型范围 | 说明 |
|------|---------|---------|------|
| PPO | policy_loss | 10-50k | 未归一化，包含多个loss component |
| DQN | TD error | 1-100 | MSE loss |
| A2C | actor_loss | -10到10 | 可能为负（基于advantage） |
| SAC | actor_loss | -100到100 | 负Q值（最大化Q） |
| TD3 | actor_loss | -100到100 | 负Q值（最大化Q） |

**结论**: Loss只用于**监控单个算法的训练趋势**，不同算法间无法比较

### 3. Reward字段说明

**当前"Reward"的含义**：
- 训练中: 环境的原始episode累积reward（经过reward_scale缩放）
- 训练后: 训练集上的平均评估reward
- **不等于最终回报率！**

**实际回报率在哪？**  
→ 前端"Training Results"部分的"Return Rate"

**建议**：
- Loss列：监控训练收敛
- Reward列：监控episode完成情况（可选，建议隐藏或改名）
- 关注最终的Return Rate（回报率）

---

## 使用建议

### 判断训练质量
1. **Loss趋势**: 应该总体下降（SAC/TD3可能为负数增长）
2. **最终Return Rate**: 正值且尽可能高
3. **Sharpe Ratio**: >1为良好，>2为优秀

### 不要比较的指标
- ❌ 不同算法的Loss绝对值
- ❌ 训练过程中的Reward绝对值

### 应该比较的指标  
- ✅ Return Rate（回报率）
- ✅ Sharpe Ratio（风险调整收益）
- ✅ Max Drawdown（最大回撤）
- ✅ Win Rate（胜率）

