# DRL Quant Trading System
# DRL 量化交易系统

<div align="center">

**基于深度强化学习的量化交易分析系统**

[English](#english) | [中文](#chinese)

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)
[![Stable-Baselines3](https://img.shields.io/badge/SB3-2.2-orange.svg)](https://stable-baselines3.readthedocs.io/)

</div>

---

## <a name="english"></a>🌟 Overview

A full-stack web application for quantitative trading analysis using Deep Reinforcement Learning (DRL) algorithms. The system enables training multiple DRL agents on stock data and backtesting their performance.

### Key Features

- 🤖 **Multiple DRL Algorithms**: PPO, DQN, A2C, SAC, TD3
- 📊 **Real-time Training Visualization**: Monitor training progress with live metrics
- 🔄 **Automated Backtesting**: Compare strategies against baseline
- 💹 **Multi-stock Portfolio**: Trade multiple stocks simultaneously
- 🎯 **Improved State/Action Space**: Advanced portfolio rebalancing with softmax weights
- 📈 **Technical Indicators**: MACD, Bollinger Bands, RSI, CCI, DX, SMA
- 🗄️ **PostgreSQL Integration**: Real stock market data via SSH tunnel

### Tech Stack

**Frontend:**
- React 18 + TypeScript
- Ant Design 5
- Recharts for visualization
- Vite

**Backend:**
- Python 3.9+
- FastAPI
- Stable-Baselines3 (DRL framework)
- PostgreSQL + SSH tunnel
- Gymnasium (RL environment)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL access (SSH tunnel configured)

### Installation

```bash
# Clone repository
git clone https://github.com/Misakavorst/drl-quant-trading.git
cd drl-quant-trading

# Backend setup
cd backend
pip install -r requirements.txt
python run.py

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000` to access the application.

📖 **Detailed guide**: See [QUICKSTART.md](QUICKSTART.md)

### Use Sample Outputs (Optional)

To quickly explore the app without running training, you can use pre-generated sample outputs:

1. Ensure the backend has created the `backend/outputs/` directory (it is auto-created on start).
2. Copy the contents of `backend/sample_outputs/` into `backend/outputs/`:

```powershell
# Windows PowerShell (from repo root)
Copy-Item -Recurse -Force backend\sample_outputs\* backend\outputs\
```

```bash
# macOS/Linux
cp -R backend/sample_outputs/* backend/outputs/
```

3. Refresh the frontend; the app will load these sample jobs from `outputs/`.

Sample job structure:

```
backend/sample_outputs/<job_id>/
├── config.json
├── progress.json
├── results.json
├── backtest_results.json
├── data/
│   ├── train.npz
│   └── test.npz
└── models/
    ├── PPO/model.zip
    ├── DQN/model.zip
    ├── A2C/model.zip
    ├── SAC/model.zip
    └── TD3/model.zip
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [QUICKSTART.md](QUICKSTART.md) | Installation and setup guide |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | Project architecture overview |
| [docs/ENVIRONMENT_REFACTOR_SUMMARY.md](docs/ENVIRONMENT_REFACTOR_SUMMARY.md) | Latest RL environment improvements |
| [backend/README.md](backend/README.md) | Backend API documentation |
| [backend/SETUP.md](backend/SETUP.md) | Backend configuration guide |
| [backend/DATABASE_SCHEMA.md](backend/DATABASE_SCHEMA.md) | Database structure |
| [docs/CHANGELOG.md](docs/CHANGELOG.md) | Version history and updates |

---

## 🎯 Usage

### 1. Stock Management
- Select stocks and date ranges
- View price charts and technical indicators

### 2. Agent Training
- Configure training parameters (timesteps, algorithms)
- Train multiple DRL agents simultaneously
- Monitor real-time training metrics (loss, reward, progress)

### 3. Backtesting
- Load trained models
- Compare DRL strategies vs baseline (Buy & Hold)
- Analyze performance metrics (return rate, Sharpe ratio, max drawdown)

---

## 🏗️ Architecture

```
drl-quant-trading/
├── backend/              # FastAPI Backend
│   ├── app/
│   │   ├── drl/         # DRL environment & training
│   │   ├── models/      # Pydantic models
│   │   ├── routers/     # API endpoints
│   │   ├── services/    # Business logic
│   │   └── utils/       # Utilities (logging, storage)
│   ├── outputs/         # Training results & models
│   └── sample_outputs/  # Pre-generated demo outputs
│
├── frontend/            # React Frontend
│   └── src/
│       ├── components/  # UI components
│       ├── pages/       # Main pages
│       └── services/    # API client
│
└── docs/               # Documentation
    ├── archive/        # Historical documentation
    └── ENVIRONMENT_REFACTOR_SUMMARY.md
```

---

## 🔬 Latest Improvements (v2.0)

### ✅ State Space Enhancement
- Added **relative price changes** (daily returns)
- Added **position ratios** (portfolio allocation)
- Improved normalization (tanh standardization)
- Reduced dimensions: 31 → 14 (for 3 stocks)

### ✅ Action Space Refactoring
- Changed to **target position ratios** (softmax normalized)
- Automatic fund constraint satisfaction
- Natural risk diversification

### ✅ DQN Optimization
- Reduced action space: 5^N → 3^N
- Example: 5 stocks = 3,125 → 243 actions (92% reduction)

**Expected improvements:**
- Training stability: +50%
- Final returns: +30-50%
- Sharpe ratio: +40-60%

---

## 📊 Performance Metrics

| Algorithm | Return Rate | Sharpe Ratio | Max Drawdown |
|-----------|-------------|--------------|--------------|
| PPO | 9.37% | 2.27 | -9.95% |
| DQN | 60.69% | 2.08 | -8.93% |
| A2C | 16.48% | 2.28 | -6.64% |
| SAC | 25.24% | 1.91 | -12.82% |
| TD3 | 54.89% | 2.08 | -16.48% |

Source: `backend/sample_outputs/401da510-0c5a-418e-9981-bfd5e365caf6` (values vary with data/settings)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is licensed under the MIT License.

---

## 📞 Contact

- GitHub: [@Misakavorst](https://github.com/Misakavorst)
- Repository: [drl-quant-trading](https://github.com/Misakavorst/drl-quant-trading)

---

---

## <a name="chinese"></a>🌟 项目简介

基于深度强化学习（DRL）算法的量化交易分析系统。该系统支持在股票数据上训练多个 DRL 智能体并回测其表现。

### 核心功能

- 🤖 **多种 DRL 算法**: PPO, DQN, A2C, SAC, TD3
- 📊 **实时训练可视化**: 实时监控训练进度和指标
- 🔄 **自动回测**: 与基线策略对比
- 💹 **多股票组合**: 同时交易多只股票
- 🎯 **改进的状态/动作空间**: 基于 softmax 的高级投资组合再平衡
- 📈 **技术指标**: MACD、布林带、RSI、CCI、DX、SMA
- 🗄️ **PostgreSQL 集成**: 通过 SSH 隧道访问真实股票市场数据

### 技术栈

**前端：**
- React 18 + TypeScript
- Ant Design 5
- Recharts 可视化
- Vite

**后端：**
- Python 3.9+
- FastAPI
- Stable-Baselines3（DRL 框架）
- PostgreSQL + SSH 隧道
- Gymnasium（强化学习环境）

---

## 🚀 快速开始

### 环境要求

- Python 3.9+
- Node.js 16+
- PostgreSQL 访问权限（SSH 隧道配置）

### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/Misakavorst/drl-quant-trading.git
cd drl-quant-trading

# 后端设置
cd backend
pip install -r requirements.txt
python run.py

# 前端设置（新终端）
cd frontend
npm install
npm run dev
```

访问 `http://localhost:3000` 使用应用。

📖 **详细指南**: 参见 [QUICKSTART.md](QUICKSTART.md)

### 使用样例输出（可选）

无需先运行训练即可快速体验应用功能，步骤如下：

1. 确认后端已创建 `backend/outputs/` 目录（启动后端时会自动创建）。
2. 将 `backend/sample_outputs/` 中的内容复制到 `backend/outputs/`：

```powershell
# Windows PowerShell（在仓库根目录执行）
Copy-Item -Recurse -Force backend\sample_outputs\* backend\outputs\
```

```bash
# macOS/Linux
cp -R backend/sample_outputs/* backend/outputs/
```

3. 刷新前端页面，应用会从 `outputs/` 目录加载这些样例任务。

样例任务目录结构示例：

```
backend/sample_outputs/<job_id>/
├── config.json
├── progress.json
├── results.json
├── backtest_results.json
├── data/
│   ├── train.npz
│   └── test.npz
└── models/
    ├── PPO/model.zip
    ├── DQN/model.zip
    ├── A2C/model.zip
    ├── SAC/model.zip
    └── TD3/model.zip
```

---

## 📚 文档

| 文档 | 说明 |
|------|------|
| [QUICKSTART.md](QUICKSTART.md) | 安装和设置指南 |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | 项目架构概览 |
| [docs/ENVIRONMENT_REFACTOR_SUMMARY.md](docs/ENVIRONMENT_REFACTOR_SUMMARY.md) | 最新环境改进 |
| [backend/README.md](backend/README.md) | 后端 API 文档 |
| [backend/SETUP.md](backend/SETUP.md) | 后端配置指南 |
| [backend/DATABASE_SCHEMA.md](backend/DATABASE_SCHEMA.md) | 数据库结构 |
| [docs/CHANGELOG.md](docs/CHANGELOG.md) | 版本历史和更新 |

---

## 🎯 使用方法

### 1. 股票管理
- 选择股票和日期范围
- 查看价格图表和技术指标

### 2. 智能体训练
- 配置训练参数（时间步、算法）
- 同时训练多个 DRL 智能体
- 监控实时训练指标（损失、奖励、进度）

### 3. 回测
- 加载训练好的模型
- 对比 DRL 策略与基线策略（买入持有）
- 分析性能指标（回报率、夏普比率、最大回撤）

---

## 🔬 最新改进（v2.0）

### ✅ 状态空间增强
- 添加**相对价格变化**（日收益率）
- 添加**持仓比例**（投资组合配置）
- 改进归一化（tanh 标准化）
- 减少维度：31 → 14（3 只股票）

### ✅ 动作空间重构
- 改为**目标仓位比例**（softmax 归一化）
- 自动满足资金约束
- 天然风险分散

### ✅ DQN 优化
- 减少动作空间：5^N → 3^N
- 示例：5 只股票 = 3,125 → 243 个动作（减少 92%）

**预期改进：**
- 训练稳定性：+50%
- 最终收益：+30-50%
- 夏普比率：+40-60%

---

## 📊 性能指标

| 算法 | 回报率 | 夏普比率 | 最大回撤 |
|------|--------|---------|---------|
| PPO | 9.37% | 2.27 | -9.95% |
| DQN | 60.69% | 2.08 | -8.93% |
| A2C | 16.48% | 2.28 | -6.64% |
| SAC | 25.24% | 1.91 | -12.82% |
| TD3 | 54.89% | 2.08 | -16.48% |

数据来源：`backend/sample_outputs/401da510-0c5a-418e-9981-bfd5e365caf6`（不同数据与参数会导致结果差异）

---

## 🤝 贡献

欢迎贡献！请随时提交 Pull Request。

---

## 📄 许可证

本项目采用 MIT 许可证。

---

## 📞 联系方式

- GitHub: [@Misakavorst](https://github.com/Misakavorst)
- 仓库: [drl-quant-trading](https://github.com/Misakavorst/drl-quant-trading)

