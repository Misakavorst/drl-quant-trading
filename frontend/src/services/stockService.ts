import api from '../utils/api'

export interface StockData {
  symbol: string
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export interface StockListRequest {
  symbols: string[]
  startDate: string
  endDate: string
}

export interface StockListResponse {
  data: StockData[]
  total: number
  symbols: string[]
  dateRange: {
    start: string
    end: string
  }
}

export interface StockOption {
  value: string
  label: string
}

export const stockService = {
  // Add stocks and fetch data
  addStocks: async (request: StockListRequest): Promise<StockListResponse> => {
    return api.post('/stocks/add', request)
  },

  // Get sample data for display
  getSampleData: async (symbols: string[], startDate: string, endDate: string): Promise<StockListResponse> => {
    return api.get('/stocks/sample', {
      params: { symbols: symbols.join(','), startDate, endDate },
    })
  },

  // Get stock list for autocomplete
  getStockList: async (search?: string): Promise<StockOption[]> => {
    return api.get('/stocks/list', {
      params: search ? { search } : {},
    })
  },
}

