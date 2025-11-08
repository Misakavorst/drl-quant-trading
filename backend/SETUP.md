# Backend Setup and Testing Guide

This guide will help you set up and test the DRL Quantitative Trading backend.

## Prerequisites

- Python 3.8 or higher
- pip
- Access to the PostgreSQL database via SSH tunnel

## Step-by-Step Setup

### 1. Create Virtual Environment (Recommended)

```bash
cd backend
python -m venv venv

# Activate on Windows
venv\Scripts\activate

# Activate on Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI and Uvicorn (web framework)
- psycopg2-binary (PostgreSQL driver)
- sshtunnel (SSH tunnel)
- Pydantic (data validation)
- Pandas, NumPy (data processing)
- PyTorch (deep learning)
- Gymnasium (RL environment)
- TA (technical analysis)

### 3. Configure Environment

The `.env` file should already be configured with the correct database credentials:

```env
# SSH Tunnel Config
SSH_HOST=kv.run
SSH_PORT=10022
SSH_USER=finai
SSH_PASSWORD=fin2025ai

# Database Config
DB_USER=postgres
DB_PASSWORD=MLsys2024
DB_NAME=fin_ai_world_model_v2
DB_HOST=localhost
DB_PORT=5432
```

### 4. Test Database Connection

Before running the full server, test the database connection:

```python
# test_db.py
from app.database import db_manager

# Start tunnel
db_manager.start_tunnel()
print("SSH tunnel started")

# Test query
schema = db_manager.inspect_schema()
print(f"Stock table columns: {len(schema['stock'])}")
print(f"Stock price table columns: {len(schema['stock_price'])}")

# Test stock query
stocks = db_manager.get_stocks_by_symbols(['AAPL'])
print(f"Found stocks: {stocks}")

# Cleanup
db_manager.stop_tunnel()
print("Connection test successful!")
```

Run it:
```bash
python test_db.py
```

### 5. Run the Server

```bash
# Option 1: Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Option 2: Using run script
python run.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     SSH tunnel started successfully
INFO:     Database schema inspected: X columns in stock table
```

### 6. Test API Endpoints

#### Test Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

#### Test Stock API

```bash
# Add stocks
curl -X POST http://localhost:8000/api/stocks/add \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["AAPL", "MSFT"],
    "startDate": "2023-01-01",
    "endDate": "2023-12-31"
  }'
```

Expected response:
```json
{
  "data": [...],
  "total": 500,
  "symbols": ["AAPL", "MSFT"],
  "dateRange": {
    "start": "2023-01-01",
    "end": "2023-12-31"
  }
}
```

#### Test Training API

```bash
# Start training
curl -X POST http://localhost:8000/api/training/start \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["AAPL"],
    "algorithms": ["PPO"]
  }'
```

Expected response:
```json
{
  "jobId": "12345678-1234-1234-1234-123456789012"
}
```

Save the jobId for next steps.

#### Get Training Progress

```bash
# Replace JOB_ID with actual job ID
curl http://localhost:8000/api/training/progress/{JOB_ID}
```

Expected response:
```json
{
  "jobId": "...",
  "progress": [
    {
      "algorithm": "PPO",
      "epoch": 500,
      "totalEpochs": 1000,
      "loss": 0.0234,
      "reward": 1500.23,
      "status": "training"
    }
  ],
  "results": []
}
```

#### Start Backtesting

```bash
curl -X POST http://localhost:8000/api/backtesting/start \
  -H "Content-Type: application/json" \
  -d '{
    "jobId": "YOUR_JOB_ID",
    "baselineStrategies": ["BuyAndHold", "MovingAverage"]
  }'
```

#### Get Backtest Results

```bash
curl http://localhost:8000/api/backtesting/results/{JOB_ID}
```

### 7. Access API Documentation

Open your browser and visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

These provide interactive API documentation.

## Frontend Integration Testing

### 1. Start Frontend

```bash
cd frontend
npm run dev
```

The frontend should be running on http://localhost:3000

### 2. Test Full Workflow

1. **Stock Management**
   - Navigate to Stock Management page
   - Add stocks: AAPL, MSFT
   - Select date range: 2023-01-01 to 2023-12-31
   - Click "Add Stocks"
   - Verify sample data appears in table

2. **Agent Training**
   - Navigate to Agent Training page
   - Enter same stock symbols: AAPL, MSFT
   - Select algorithms: PPO, DQN
   - Click "Start Training"
   - Verify training progress updates
   - Wait for training to complete

3. **Backtesting**
   - Navigate to Backtesting page
   - Enter the training job ID
   - Select baseline strategies
   - Click "Start Backtesting"
   - Wait for results
   - Verify charts and comparison tables

## Troubleshooting

### SSH Tunnel Fails

**Error**: `Connection refused` or `Authentication failed`

**Solution**:
1. Check SSH credentials in `.env`
2. Test SSH manually: `ssh -p 10022 finai@kv.run`
3. Check if port 10022 is open
4. Verify network connectivity

### Database Query Fails

**Error**: `relation "stock" does not exist`

**Solution**:
1. Verify database name in `.env`
2. Check if you have the correct database
3. Run schema inspection to verify tables exist

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'elegantrl'`

**Solution**:
1. Check that ElegantRL-master folder exists in project root
2. Verify Python path is set correctly
3. Try: `pip install elegantrl`

### Port Already in Use

**Error**: `Address already in use`

**Solution**:
```bash
# Find process using port 8000
# Windows
netstat -ano | findstr :8000

# Linux/Mac
lsof -i :8000

# Kill the process or use different port
uvicorn app.main:app --reload --port 8001
```

### Training Takes Too Long

**Issue**: Training is very slow

**Solution**:
1. Reduce `max_step` in training_service.py
2. Use fewer stocks for testing
3. Reduce date range
4. Check if GPU is being used: `torch.cuda.is_available()`

### Memory Issues

**Issue**: Out of memory during training

**Solution**:
1. Reduce batch size
2. Use fewer stocks
3. Reduce network size (net_dims)
4. Close other applications

## Performance Tuning

### Training Parameters

Edit `app/services/training_service.py`:

```python
# For faster testing (less accuracy)
args.max_step = 1e4  # Instead of 5e5
args.batch_size = 128  # Instead of 512

# For production (better accuracy, slower)
args.max_step = 1e6
args.batch_size = 1024
```

### Database Query Optimization

For large datasets, consider:
1. Adding database indexes on `stock_id` and `date`
2. Using query result caching
3. Fetching data in batches

## Next Steps

1. Implement actual ElegantRL training loop
2. Add model saving and loading
3. Implement more sophisticated baseline strategies
4. Add logging and monitoring
5. Add unit tests and integration tests
6. Add authentication and authorization
7. Deploy to production server

## Support

For issues or questions:
1. Check logs in console output
2. Review API documentation at /docs
3. Check database connection status at /health

