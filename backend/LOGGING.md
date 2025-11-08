# 日志系统说明

## 概述

后端训练和回测系统已配置完整的日志记录功能，所有关键步骤和错误都会被记录到日志文件中。

## 日志文件位置

所有日志文件存储在 `backend/logs/` 目录下：

```
backend/logs/
├── training_service_YYYYMMDD.log      # 训练服务主日志
├── backtest_service_YYYYMMDD.log      # 回测服务主日志
├── trainer_YYYYMMDD.log               # DRL训练器日志
├── environment_YYYYMMDD.log           # 环境日志
├── training_<job_id>.log              # 特定训练任务的详细日志
└── backtest_<job_id>.log              # 特定回测任务的详细日志
```

## 日志级别

- **DEBUG**: 详细的调试信息
- **INFO**: 关键步骤和进度信息
- **WARNING**: 警告信息（不影响运行）
- **ERROR**: 错误信息（含完整堆栈跟踪）

## 日志内容

### 训练服务日志 (`training_service.log`)

记录内容：
- ✅ 训练任务初始化
- ✅ 配置参数（股票、算法、日期范围等）
- ✅ 数据加载和环境创建
- ✅ 训练器初始化
- ✅ 训练进度和指标更新
- ✅ 测试集评估结果
- ✅ 最终性能指标
- ✅ 所有错误和异常

示例日志：
```
2025-01-09 10:30:15 - INFO - ================================================================================
2025-01-09 10:30:15 - INFO - STARTING TRAINING JOB: abc123...
2025-01-09 10:30:15 - INFO - Parameters:
2025-01-09 10:30:15 - INFO -   Symbols: ['AAPL']
2025-01-09 10:30:15 - INFO -   Algorithms: ['PPO', 'DQN']
2025-01-09 10:30:15 - INFO -   Date Range: 2022-11-09 to 2025-11-09
```

### DRL训练器日志 (`trainer.log`)

记录内容：
- ✅ 训练器初始化（算法、设备、网络参数）
- ✅ Agent创建和配置
- ✅ Replay buffer初始化（off-policy算法）
- ✅ 训练循环进度
- ✅ 定期评估结果
- ✅ 模型保存信息
- ✅ 最终训练统计

示例日志：
```
2025-01-09 10:30:20 - INFO - ======================================================================
2025-01-09 10:30:20 - INFO - INITIALIZING DRL TRAINER
2025-01-09 10:30:20 - INFO - Algorithm: PPO
2025-01-09 10:30:20 - INFO - Device: cuda:0
2025-01-09 10:30:20 - INFO - Environment: state_dim=11, action_dim=1, max_step=548
```

### 回测服务日志 (`backtest_service.log`)

记录内容：
- ✅ 回测任务初始化
- ✅ 测试数据加载
- ✅ 每个算法的回测进度
- ✅ 基线策略执行
- ✅ 性能指标对比
- ✅ 最佳算法分析
- ✅ 结果保存确认

示例日志：
```
2025-01-09 10:45:00 - INFO - ================================================================================
2025-01-09 10:45:00 - INFO - STARTING BACKTESTING
2025-01-09 10:45:00 - INFO - Job ID: abc123...
2025-01-09 10:45:00 - INFO - Baseline Strategies: ['BuyAndHold', 'MovingAverage']
```

### 任务特定日志 (`training_<job_id>.log` / `backtest_<job_id>.log`)

每个训练/回测任务都有独立的日志文件，包含该任务的所有详细信息：
- 完整的配置参数
- 每一步的详细进度
- 所有中间结果
- 完整的错误堆栈（如果有）

## 使用方法

### 查看最新日志

```bash
# 查看训练服务日志
Get-Content backend\logs\training_service_*.log -Tail 50

# 查看特定任务的日志
Get-Content backend\logs\training_<job_id>.log

# 实时监控日志
Get-Content backend\logs\training_service_*.log -Wait
```

### 搜索错误

```bash
# 搜索所有错误
Select-String -Path backend\logs\*.log -Pattern "ERROR"

# 搜索特定任务的错误
Select-String -Path backend\logs\training_<job_id>.log -Pattern "ERROR|Exception"
```

### 分析训练进度

```bash
# 查看所有评估结果
Select-String -Path backend\logs\trainer_*.log -Pattern "EVALUATION"

# 查看训练完成的任务
Select-String -Path backend\logs\training_*.log -Pattern "TRAINING COMPLETED"
```

## 日志格式

### 文件日志格式（详细）
```
YYYY-MM-DD HH:MM:SS - module_name - LEVEL - [filename:lineno] - message
```

### 控制台日志格式（简洁）
```
YYYY-MM-DD HH:MM:SS - LEVEL - message
```

## 调试建议

### 训练失败时

1. 检查训练服务日志：
   ```bash
   Get-Content backend\logs\training_service_*.log | Select-String -Pattern "ERROR|failed"
   ```

2. 查看特定任务日志：
   ```bash
   Get-Content backend\logs\training_<job_id>.log
   ```

3. 检查trainer日志中的详细错误：
   ```bash
   Get-Content backend\logs\trainer_*.log | Select-String -Pattern "ERROR" -Context 5
   ```

### 回测结果异常时

1. 检查回测服务日志：
   ```bash
   Get-Content backend\logs\backtest_service_*.log | Select-String -Pattern "ERROR|WARNING"
   ```

2. 查看特定回测任务日志：
   ```bash
   Get-Content backend\logs\backtest_<job_id>.log
   ```

3. 确认模型是否正确加载：
   ```bash
   Select-String -Path backend\logs\backtest_*.log -Pattern "Loading model"
   ```

## 日志保留

- 日志文件按日期命名，不会自动删除
- 建议定期清理旧日志文件（如保留最近30天）
- 重要任务的日志可以备份保存

## 配置

日志配置位于 `backend/app/utils/logger.py`：

- 日志级别：默认 DEBUG
- 文件编码：UTF-8
- 时间格式：`YYYY-MM-DD HH:MM:SS`
- 自动创建logs目录

## 性能影响

- 日志系统对性能影响极小（< 1%）
- DEBUG级别日志仅输出到文件，不显示在控制台
- 可通过环境变量 `LOG_LEVEL` 调整日志级别

```bash
# 仅记录INFO及以上级别
$env:LOG_LEVEL="INFO"
python run.py
```

## 故障排查检查清单

训练/回测失败时，按顺序检查：

1. ✅ 查看控制台输出中的ERROR信息
2. ✅ 检查训练服务日志中的错误
3. ✅ 查看特定任务的详细日志
4. ✅ 检查数据加载是否成功
5. ✅ 确认环境创建无误
6. ✅ 验证模型保存路径
7. ✅ 检查GPU/内存资源

所有这些信息都已详细记录在日志文件中！

