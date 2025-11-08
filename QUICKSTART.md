# Quick Start Guide

Get the DRL Quantitative Trading system up and running in 5 minutes.

## Prerequisites

- Python 3.8+
- Node.js 16+
- pip and npm

## Backend Setup (2 minutes)

```bash
# 1. Navigate to backend
cd backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create outputs directory
mkdir -p outputs

# 4. Run the server
python run.py
```

Server will start on `http://localhost:8000`

✅ Test: Visit `http://localhost:8000/health` - should see `{"status":"healthy"}`

## Frontend Setup (2 minutes)

```bash
# 1. Navigate to frontend (in new terminal)
cd frontend

# 2. Install dependencies
npm install

# 3. Run the dev server
npm run dev
```

Frontend will start on `http://localhost:3000`

✅ Test: Visit `http://localhost:3000` - should see the app

## First Run Test (3 minutes)

### 1. Add Stocks
- Navigate to **Stock Management**
- Enter stocks: `AAPL, MSFT`
- Select date range: `2023-01-01` to `2023-12-31`
- Click **Add Stocks**
- ✅ Sample data should appear in table

### 2. Train Agent
- Navigate to **Agent Training**
- Enter same stocks: `AAPL, MSFT`
- Select algorithm: `PPO`
- Click **Start Training**
- ✅ Training progress should update every few seconds

### 3. View Backtest
- Navigate to **Backtesting**
- Enter the training job ID (from training page)
- Select baseline: `BuyAndHold`
- Click **Start Backtesting**
- ✅ Charts and comparison should appear

## Troubleshooting

### Backend won't start

**SSH Tunnel Error**:
```bash
# Test database connection
cd backend
python test_db.py
```

If connection fails, check:
- SSH credentials in `backend/.env`
- Network connectivity
- Firewall settings

### Frontend won't start

**Port in use**:
```bash
# Edit frontend/vite.config.ts
# Change port from 3000 to 3001
```

### API calls fail

**CORS Error**:
- Check backend is running on port 8000
- Check frontend proxy settings in `vite.config.ts`

**404 Error**:
- Verify API prefix is `/api` in both frontend and backend

## API Documentation

Once backend is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Configuration

### Change Database
Edit `backend/.env`:
```env
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password
```

### Change Training Parameters
Edit `backend/app/config.py`:
```python
train_test_split: float = 0.8  # 80% train, 20% test
initial_amount: float = 1e6    # $1,000,000 starting capital
```

### Change Algorithms
Edit training request to include:
- `PPO` - Proximal Policy Optimization
- `DQN` - Deep Q-Network
- `SAC` - Soft Actor-Critic
- `TD3` - Twin Delayed DDPG
- `A2C` - Advantage Actor-Critic

## Next Steps

1. ✅ **Test with real data**: Use actual stock symbols from your database
2. 📚 **Read documentation**: Check `backend/SETUP.md` for detailed guide
3. 🔧 **Customize**: Modify training parameters, add new algorithms
4. 📊 **Analyze**: Compare different strategies and parameters
5. 🚀 **Deploy**: Follow deployment guide for production

## Support Files

- **Backend Setup**: `backend/SETUP.md`
- **Backend README**: `backend/README.md`
- **Frontend README**: `frontend/README.md`
- **Project Summary**: `PROJECT_SUMMARY.md`
- **API Documentation**: http://localhost:8000/docs (when running)

## Common Commands

```bash
# Backend
cd backend
python run.py                 # Start server
python test_db.py             # Test database
pip install -r requirements.txt  # Install deps

# Frontend
cd frontend
npm run dev                   # Start dev server
npm run build                 # Build for production
npm install                   # Install deps

# Check processes
# Windows
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# Linux/Mac
lsof -i :8000
lsof -i :3000
```

## Success Checklist

- [ ] Backend server running on port 8000
- [ ] Frontend app running on port 3000
- [ ] Database connection successful (`/health` returns healthy)
- [ ] Can add stocks and see sample data
- [ ] Can start training and see progress
- [ ] Can run backtest and see charts
- [ ] API documentation accessible at `/docs`

🎉 **You're ready to go!** Start exploring the DRL trading system.

## Need Help?

1. Check `backend/SETUP.md` for detailed troubleshooting
2. Review API docs at http://localhost:8000/docs
3. Test database connection with `python test_db.py`
4. Check console logs for error messages

