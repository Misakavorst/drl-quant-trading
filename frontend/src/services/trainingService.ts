import api from '../utils/api'

export interface TrainingConfig {
  symbols: string[]
  algorithms: string[] // e.g., ['PPO', 'DQN', 'A2C']
  startDate?: string   // Format: YYYY-MM-DD
  endDate?: string     // Format: YYYY-MM-DD
  trainTestSplit?: number  // 0-1, e.g., 0.8 for 80% train, 20% test
  totalTimesteps?: number  // Total training timesteps (default: 10000)
}

export interface TrainingProgress {
  algorithm: string
  epoch: number
  totalEpochs: number
  loss: number
  reward: number
  status: 'pending' | 'training' | 'completed' | 'failed'
}

export interface TrainingResult {
  algorithm: string
  status: 'completed' | 'failed'
  metrics: {
    totalReward: number
    sharpeRatio: number
    maxDrawdown: number
    winRate: number
    initialAmount: number
    finalAmount: number
    returnRate: number
  }
  trainingTime: number
  modelPath: string
}

export interface TrainingResponse {
  jobId: string
  progress: TrainingProgress[]
  results: TrainingResult[]
}

export interface TrainingHistoryItem {
  jobId: string
  symbols: string[]
  algorithms: string[]
  startDate?: string
  endDate?: string
  trainTestSplit?: number
  createdAt: string
  completed: boolean
}

export const trainingService = {
  // Start training
  startTraining: async (config: TrainingConfig): Promise<{ jobId: string }> => {
    return api.post('/training/start', config)
  },

  // Get training progress
  getProgress: async (jobId: string): Promise<TrainingResponse> => {
    return api.get(`/training/progress/${jobId}`)
  },

  // Get training results
  getResults: async (jobId: string): Promise<TrainingResponse> => {
    return api.get(`/training/results/${jobId}`)
  },

  // Get training history
  getHistory: async (): Promise<TrainingHistoryItem[]> => {
    return api.get('/training/history')
  },
}

