# DRL Quantitative Trading Analysis - Frontend

A modern web application for Deep Reinforcement Learning (DRL) based quantitative trading analysis. This is the frontend part of a full-stack application that allows users to manage stock data, train DRL agents, and perform backtesting with comprehensive visualizations.

## Features

### 1. Stock Management
- Add and manage stock symbols
- Select date ranges for data retrieval
- View sample stock data in a table format
- Real-time data fetching from backend

### 2. Agent Training
- Configure and train multiple DRL algorithms (PPO, DQN, A2C, SAC, TD3)
- Real-time training progress monitoring
- Training metrics display (loss, reward, Sharpe ratio, etc.)
- Train/test data split configuration

### 3. Backtesting
- Run backtests using trained agents
- Compare DRL algorithms with baseline strategies
- Multiple visualization charts:
  - Cumulative returns comparison
  - Daily returns analysis
  - Metrics comparison (returns, Sharpe ratio, drawdown, win rate)
- Comprehensive performance metrics table

## Technology Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Ant Design 5** - UI component library
- **Recharts** - Chart visualization
- **React Router** - Navigation
- **Axios** - HTTP client
- **Vite** - Build tool
- **Day.js** - Date handling

## Project Structure

```
src/
├── components/
│   └── Layout/
│       └── AppLayout.tsx      # Main layout with navigation
├── pages/
│   ├── StockManagement.tsx    # Stock data management page
│   ├── AgentTraining.tsx      # DRL agent training page
│   └── Backtesting.tsx        # Backtesting and comparison page
├── services/
│   ├── stockService.ts        # Stock data API service
│   ├── trainingService.ts     # Training API service
│   └── backtestingService.ts  # Backtesting API service
├── utils/
│   └── api.ts                 # Axios configuration
├── App.tsx                    # Main app component with routing
├── main.tsx                   # Application entry point
└── index.css                  # Global styles
```

## Getting Started

### Prerequisites

- Node.js 16+ and npm/yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

### Build for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

## API Configuration

The frontend expects the backend API to be running on `http://localhost:8000`. The API proxy is configured in `vite.config.ts`. You can modify the proxy settings if your backend runs on a different port.

### Expected API Endpoints

#### Stock Service
- `POST /api/stocks/add` - Add stocks and fetch data
- `GET /api/stocks/sample` - Get sample data

#### Training Service
- `POST /api/training/start` - Start training
- `GET /api/training/progress/:jobId` - Get training progress
- `GET /api/training/results/:jobId` - Get training results

#### Backtesting Service
- `POST /api/backtesting/start` - Start backtesting
- `GET /api/backtesting/results/:jobId` - Get backtest results

## Usage

1. **Stock Management**: Navigate to the home page, add stock symbols (comma-separated), select a date range, and click "Add Stocks" to fetch data from the backend.

2. **Agent Training**: Go to the "Agent Training" page, configure your training parameters (algorithms, date range, train/test split), and start training. Monitor progress in real-time.

3. **Backtesting**: On the "Backtesting" page, enter the training job ID, select stocks and date range, choose baseline strategies for comparison, and run backtests. View comprehensive charts and metrics.

## Development

The project uses ESLint for code quality. Run linting with:

```bash
npm run lint
```

## License

MIT

