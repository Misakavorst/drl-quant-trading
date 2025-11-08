# DRL Quantitative Trading Backend

Backend API server for Deep Reinforcement Learning based quantitative trading analysis.

## Features

- SSH tunnel connection to PostgreSQL database
- Stock data fetching with technical indicators
- DRL agent training using ElegantRL
- Backtesting with multiple algorithms
- Baseline strategy comparison
- RESTful API with FastAPI

## Tech Stack

- **FastAPI** - Modern web framework
- **PostgreSQL** - Database (via SSH tunnel)
- **ElegantRL** - DRL algorithms
- **PyTorch** - Deep learning
- **Pandas** - Data processing
- **TA** - Technical indicators

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database & SSH tunnel
│   ├── models/              # Pydantic models
│   │   ├── stock.py
│   │   ├── training.py
│   │   └── backtesting.py
│   ├── routers/             # API endpoints
│   │   ├── stocks.py
│   │   ├── training.py
│   │   └── backtesting.py
│   ├── services/            # Business logic
│   │   ├── data_service.py
│   │   ├── training_service.py
│   │   └── backtest_service.py
│   ├── drl/                 # DRL components
│   │   └── stock_env.py
│   └── utils/
│       └── storage.py
├── outputs/                 # Training outputs
├── requirements.txt
└── .env
```

## Installation

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and update if needed:

```bash
cp .env.example .env
```

The default configuration connects to the specified database via SSH tunnel.

### 3. Run the Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use the run script
python run.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check

- `GET /` - Root endpoint
- `GET /health` - Health check with database status

### Stock Management

- `POST /api/stocks/add` - Add stocks and fetch data
  ```json
  {
    "symbols": ["AAPL", "MSFT"],
    "startDate": "2020-01-01",
    "endDate": "2023-12-31"
  }
  ```

- `GET /api/stocks/sample` - Get sample data
  - Query params: `symbols`, `startDate`, `endDate`

### Training

- `POST /api/training/start` - Start training
  ```json
  {
    "symbols": ["AAPL", "MSFT"],
    "algorithms": ["PPO", "DQN", "SAC"]
  }
  ```
  Returns: `{"jobId": "uuid"}`

- `GET /api/training/progress/{jobId}` - Get training progress
- `GET /api/training/results/{jobId}` - Get training results

### Backtesting

- `POST /api/backtesting/start` - Start backtesting
  ```json
  {
    "jobId": "training-job-id",
    "baselineStrategies": ["BuyAndHold", "MovingAverage"]
  }
  ```

- `GET /api/backtesting/results/{jobId}` - Get backtest results

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Output Structure

Training and backtesting results are saved in the `outputs/` directory:

```
outputs/
└── {job_id}/
    ├── config.json          # Job configuration
    ├── data/
    │   ├── train.npz       # Training data
    │   └── test.npz        # Testing data
    ├── models/
    │   ├── PPO/            # Trained PPO model
    │   ├── DQN/            # Trained DQN model
    │   └── ...
    ├── progress.json        # Training progress
    ├── results.json         # Training results
    └── backtest_results.json # Backtest results
```

## Database Schema

The backend expects the following PostgreSQL tables:

### `stock` table
- `id` - Stock ID
- `symbol` - Stock symbol (e.g., 'AAPL')
- `name` - Company name

### `stock_price` table
- `id` - Record ID
- `stock_id` - Foreign key to stock
- `date` - Trading date
- `open` - Opening price
- `high` - High price
- `low` - Low price
- `close` - Closing price
- `volume` - Trading volume

## Technical Indicators

The following technical indicators are calculated:
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands (Upper and Lower)
- RSI 30 (Relative Strength Index)
- CCI 30 (Commodity Channel Index)
- DX 30 (Directional Index)
- SMA 30 (30-day Simple Moving Average)
- SMA 60 (60-day Simple Moving Average)

## DRL Algorithms

Supported algorithms:
- **PPO** - Proximal Policy Optimization
- **DQN** - Deep Q-Network
- **SAC** - Soft Actor-Critic
- **TD3** - Twin Delayed DDPG
- **A2C** - Advantage Actor-Critic

## Baseline Strategies

Implemented baseline strategies:
- **BuyAndHold** - Buy all stocks at start and hold
- **MovingAverage** - Trade based on moving average signals
- **Random** - Random trading actions
- **EqualWeight** - Equal weight rebalancing

## Configuration

Key configuration options in `.env`:

```env
# SSH Tunnel
SSH_HOST=kv.run
SSH_PORT=10022
SSH_USER=finai
SSH_PASSWORD=fin2025ai

# Database
DB_USER=postgres
DB_PASSWORD=MLsys2024
DB_NAME=fin_ai_world_model_v2
DB_HOST=localhost
DB_PORT=5432

# Training
TRAIN_TEST_SPLIT=0.8
INITIAL_AMOUNT=1000000
MAX_STOCK=100
TRANSACTION_COST_PCT=0.001
```

## Development

### Run Tests

```bash
pytest
```

### Check Code Quality

```bash
# Format code
black app/

# Type checking
mypy app/

# Linting
flake8 app/
```

## Troubleshooting

### SSH Tunnel Connection Issues

If you encounter connection issues:
1. Verify SSH credentials in `.env`
2. Check if the SSH port is accessible
3. Test SSH connection manually: `ssh -p 10022 finai@kv.run`

### Database Connection Issues

1. Ensure PostgreSQL is running on remote server
2. Verify database credentials
3. Check firewall rules

### Training Issues

1. Ensure sufficient disk space in `outputs/` directory
2. Check GPU availability: `torch.cuda.is_available()`
3. Monitor memory usage during training

## License

MIT

