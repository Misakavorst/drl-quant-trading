# DRL Quantitative Trading System - Project Summary

## Overview

A full-stack web application for Deep Reinforcement Learning (DRL) based quantitative trading analysis. The system allows users to manage stock data, train DRL trading agents, and perform comprehensive backtesting with visualization.

## Architecture

### Frontend (React + TypeScript)
- **Framework**: React 18 with TypeScript
- **UI Library**: Ant Design 5
- **Charts**: Recharts
- **Routing**: React Router v6
- **State Management**: React hooks
- **Build Tool**: Vite

#### Key Features:
1. **Stock Management**: Add stocks, select date ranges, view sample data
2. **Agent Training**: Configure and monitor DRL agent training in real-time
3. **Backtesting**: Visualize and compare DRL algorithms vs baseline strategies

### Backend (Python + FastAPI)
- **Framework**: FastAPI
- **Database**: PostgreSQL (via SSH tunnel)
- **DRL Library**: ElegantRL
- **ML Framework**: PyTorch
- **Data Processing**: Pandas, NumPy
- **Technical Analysis**: TA library

#### Key Components:
1. **Database Service**: SSH tunnel + PostgreSQL connection
2. **Data Service**: Fetch data, calculate technical indicators
3. **Training Service**: DRL agent training with multiple algorithms
4. **Backtest Service**: Model evaluation and strategy comparison
5. **Custom Environment**: Stock trading environment for RL

## Technology Stack

### Frontend
```
React 18.2.0
TypeScript 5.2.2
Ant Design 5.11.0
Recharts 2.10.3
Axios 1.6.2
React Router 6.20.0
Vite 4.5.0
```

### Backend
```
FastAPI 0.104.1
PyTorch 2.1.0
Pandas 2.1.3
NumPy 1.24.3
psycopg2-binary 2.9.9
sshtunnel 0.4.0
Pydantic 2.5.0
TA 0.11.0
Gymnasium 0.29.1
```

## API Endpoints

### Stock Management
- `POST /api/stocks/add` - Add stocks and fetch historical data
- `GET /api/stocks/sample` - Get sample data for display

### Training
- `POST /api/training/start` - Start training job
- `GET /api/training/progress/{jobId}` - Get real-time progress
- `GET /api/training/results/{jobId}` - Get final results

### Backtesting
- `POST /api/backtesting/start` - Start backtesting
- `GET /api/backtesting/results/{jobId}` - Get backtest results

## DRL Algorithms

Implemented:
- **PPO** (Proximal Policy Optimization)
- **DQN** (Deep Q-Network)
- **SAC** (Soft Actor-Critic)
- **TD3** (Twin Delayed DDPG)
- **A2C** (Advantage Actor-Critic)

## Baseline Strategies

For comparison:
- **Buy and Hold**: Purchase stocks at start, hold until end
- **Moving Average**: Trade based on MA crossover signals
- **Random**: Random trading actions
- **Equal Weight**: Daily portfolio rebalancing

## Technical Indicators

Calculated for each stock:
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands (Upper/Lower)
- RSI 30 (Relative Strength Index)
- CCI 30 (Commodity Channel Index)
- DX 30 (Directional Index)
- SMA 30/60 (Simple Moving Averages)

## State Space Design

The RL environment uses:
- **Cash amount** (1 dimension)
- **Shares per stock** (N dimensions)
- **Close prices** (N dimensions)
- **Technical indicators** (M dimensions per stock)

Total state dimension: 1 + 2N + M

## File Storage Structure

```
outputs/
└── {job_id}/
    ├── config.json          # Job configuration
    ├── data/
    │   ├── train.npz       # Training data
    │   └── test.npz        # Testing data
    ├── models/
    │   ├── PPO/            # Trained models
    │   ├── DQN/
    │   └── ...
    ├── progress.json        # Real-time training progress
    ├── results.json         # Final training results
    └── backtest_results.json # Backtesting results
```

## Database Schema

### `stock` table
- id (primary key)
- symbol (stock ticker)
- name (company name)

### `stock_price` table
- id (primary key)
- stock_id (foreign key)
- date (trading date)
- open, high, low, close (prices)
- volume (trading volume)

## Workflow

1. **Data Collection**
   - User selects stocks and date range
   - Backend fetches data from database via SSH tunnel
   - Technical indicators calculated
   - Sample data displayed in frontend

2. **Training**
   - User selects algorithms to train
   - Data split into train/test sets (80/20)
   - Each algorithm trains independently
   - Progress updated in real-time
   - Models saved to disk

3. **Backtesting**
   - Load trained models
   - Run on test data
   - Calculate performance metrics
   - Compare with baseline strategies
   - Visualize results with charts

## Key Metrics

### Training Metrics
- Total Reward
- Sharpe Ratio
- Max Drawdown
- Win Rate
- Training Time

### Backtest Metrics
- Total Return
- Sharpe Ratio
- Max Drawdown
- Volatility
- Win Rate
- Daily Returns
- Cumulative Returns

## Configuration

### Database Connection (SSH Tunnel)
```
SSH Host: kv.run
SSH Port: 10022
SSH User: finai
Database: fin_ai_world_model_v2
```

### Training Parameters
```
Train/Test Split: 80/20
Initial Capital: $1,000,000
Max Stock per Trade: 100 shares
Transaction Cost: 0.1%
Discount Factor (γ): 0.99
```

## Running the System

### Backend
```bash
cd backend
pip install -r requirements.txt
python run.py
# Server runs on http://localhost:8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
# App runs on http://localhost:3000
```

## Features Implemented

✅ Frontend with 3 main pages
✅ Backend API with FastAPI
✅ SSH tunnel to PostgreSQL database
✅ Data fetching with technical indicators
✅ Custom DRL environment
✅ Multiple DRL algorithm support
✅ Training progress tracking
✅ Backtesting engine
✅ Baseline strategy comparison
✅ Real-time progress updates
✅ File-based result storage
✅ Comprehensive API documentation
✅ Error handling and logging

## Future Enhancements

- [ ] Implement full ElegantRL training loop
- [ ] Add model persistence and loading
- [ ] GPU acceleration for training
- [ ] More sophisticated baseline strategies
- [ ] User authentication
- [ ] Training history and comparison
- [ ] Real-time trading simulation
- [ ] Portfolio optimization
- [ ] Risk management features
- [ ] Deployment configuration
- [ ] Unit and integration tests
- [ ] Performance monitoring
- [ ] Database query optimization
- [ ] Caching layer

## Project Structure

```
drl-quant-trading-workspace/
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # UI components
│   │   ├── pages/         # Main pages
│   │   ├── services/      # API services
│   │   └── utils/         # Utilities
│   └── package.json
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── routers/      # API endpoints
│   │   ├── services/     # Business logic
│   │   ├── models/       # Data models
│   │   ├── drl/          # DRL components
│   │   └── utils/        # Utilities
│   ├── outputs/          # Training outputs
│   └── requirements.txt
├── ElegantRL-master/     # DRL library
└── PROJECT_SUMMARY.md    # This file
```

## Documentation

- **Frontend README**: `/frontend/README.md`
- **Backend README**: `/backend/README.md`
- **Setup Guide**: `/backend/SETUP.md`
- **API Docs**: `http://localhost:8000/docs` (when running)

## License

MIT

