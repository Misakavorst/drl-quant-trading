import api from '../utils/api'

export interface BacktestConfig {
  jobId: string // Training job ID to get trained models
  baselineStrategies?: string[] // e.g., ['BuyAndHold', 'MovingAverage']
  force?: boolean // Force re-run even if results exist
}

export interface BacktestResult {
  algorithm: string
  type: 'drl' | 'baseline'
  returns: number[]
  cumulativeReturns: number[]
  dates: string[]
  metrics: {
    totalReturn: number
    sharpeRatio: number
    maxDrawdown: number
    volatility: number
    winRate: number
  }
}

export interface BacktestResponse {
  jobId: string
  results: BacktestResult[]
  comparison: {
    bestAlgorithm: string
    bestReturn: number
    bestSharpeRatio: number
  }
}

export const backtestingService = {
  // Start backtesting
  startBacktest: async (config: BacktestConfig): Promise<{ jobId: string }> => {
    return api.post('/backtesting/start', config)
  },

  // Get backtest results
  getResults: async (jobId: string): Promise<BacktestResponse> => {
    return api.get(`/backtesting/results/${jobId}`)
  },
}

