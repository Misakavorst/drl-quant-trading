"""Data fetching and processing service"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
import logging
from ta import add_all_ta_features
from ta.trend import MACD, SMAIndicator
from ta.volatility import BollingerBands
from ta.momentum import RSIIndicator

from ..database import db_manager
from ..config import settings

logger = logging.getLogger(__name__)


class DataService:
    """Service for fetching and processing stock data"""
    
    def __init__(self):
        self.db = db_manager
    
    def fetch_and_prepare_data(
        self, 
        symbols: List[str], 
        start_date: str, 
        end_date: str
    ) -> Dict[str, Any]:
        """
        Fetch stock data from database and calculate technical indicators
        
        Returns:
            {
                'close_ary': np.array (days, stocks),
                'tech_ary': np.array (days, features),
                'raw_data': list of dicts,
                'symbols': list of symbols,
                'dates': list of dates
            }
        """
        # Get stock information
        stocks = self.db.get_stocks_by_symbols(symbols)
        if not stocks:
            raise ValueError(f"No stocks found for symbols: {symbols}")
        
        symbol_to_id = {stock['symbol']: stock['id'] for stock in stocks}
        stock_ids = [stock['id'] for stock in stocks]
        
        # Fetch price data
        prices = self.db.get_multiple_stock_prices(stock_ids, start_date, end_date)
        if not prices:
            raise ValueError(f"No price data found for date range {start_date} to {end_date}")
        
        logger.info(f"Fetched {len(prices)} price records for {len(symbols)} stocks")
        
        # Convert to DataFrame for easier processing
        df = pd.DataFrame(prices)
        df['date'] = pd.to_datetime(df['date'])
        
        # Create a pivot table for each price field
        close_df = df.pivot(index='date', columns='stock_id', values='close')
        high_df = df.pivot(index='date', columns='stock_id', values='high')
        low_df = df.pivot(index='date', columns='stock_id', values='low')
        volume_df = df.pivot(index='date', columns='stock_id', values='volume')
        open_df = df.pivot(index='date', columns='stock_id', values='open')
        
        # Sort by date
        close_df = close_df.sort_index()
        high_df = high_df.sort_index()
        low_df = low_df.sort_index()
        volume_df = volume_df.sort_index()
        open_df = open_df.sort_index()
        
        # Fill missing values (forward fill then backward fill)
        close_df = close_df.fillna(method='ffill').fillna(method='bfill')
        high_df = high_df.fillna(method='ffill').fillna(method='bfill')
        low_df = low_df.fillna(method='ffill').fillna(method='bfill')
        volume_df = volume_df.fillna(method='ffill').fillna(method='bfill')
        open_df = open_df.fillna(method='ffill').fillna(method='bfill')
        
        # Calculate technical indicators for each stock
        tech_features_list = []
        
        for stock_id in stock_ids:
            # Create a temporary dataframe for this stock
            stock_df = pd.DataFrame({
                'close': close_df[stock_id],
                'high': high_df[stock_id],
                'low': low_df[stock_id],
                'volume': volume_df[stock_id],
                'open': open_df[stock_id]
            })
            
            # Calculate technical indicators
            # MACD
            macd = MACD(close=stock_df['close'])
            macd_values = macd.macd().values
            
            # Bollinger Bands
            bollinger = BollingerBands(close=stock_df['close'])
            boll_ub = bollinger.bollinger_hband().values
            boll_lb = bollinger.bollinger_lband().values
            
            # RSI
            rsi = RSIIndicator(close=stock_df['close'], window=30)
            rsi_30 = rsi.rsi().values
            
            # CCI (Commodity Channel Index) - use approximate calculation
            tp = (stock_df['high'] + stock_df['low'] + stock_df['close']) / 3
            cci_30 = ((tp - tp.rolling(window=30).mean()) / 
                      (0.015 * tp.rolling(window=30).std())).values
            
            # DX (Directional Index) - simplified version
            dx_30 = np.ones_like(macd_values) * 50  # Placeholder
            
            # Moving averages
            close_30_sma = SMAIndicator(close=stock_df['close'], window=30).sma_indicator().values
            close_60_sma = SMAIndicator(close=stock_df['close'], window=60).sma_indicator().values
            
            # Stack all features for this stock
            stock_features = np.column_stack([
                macd_values,
                boll_ub,
                boll_lb,
                rsi_30,
                cci_30,
                dx_30,
                close_30_sma,
                close_60_sma
            ])
            
            tech_features_list.append(stock_features)
        
        # Concatenate all technical features
        # Shape: (days, stocks * features)
        tech_ary = np.concatenate(tech_features_list, axis=1)
        
        # Fill NaN values with 0 (from indicators at the start)
        tech_ary = np.nan_to_num(tech_ary, 0)
        
        # Get close array
        close_ary = close_df.values
        
        # Prepare raw data for frontend (first 20 rows as sample)
        raw_data = []
        dates = close_df.index.strftime('%Y-%m-%d').tolist()
        
        for i, date_str in enumerate(dates[:20]):  # First 20 rows
            for symbol, stock_id in symbol_to_id.items():
                col_idx = stock_ids.index(stock_id)
                raw_data.append({
                    'symbol': symbol,
                    'date': date_str,
                    'open': float(open_df.iloc[i, col_idx]),
                    'high': float(high_df.iloc[i, col_idx]),
                    'low': float(low_df.iloc[i, col_idx]),
                    'close': float(close_df.iloc[i, col_idx]),
                    'volume': int(volume_df.iloc[i, col_idx])
                })
        
        return {
            'close_ary': close_ary,
            'tech_ary': tech_ary,
            'raw_data': raw_data,
            'symbols': symbols,
            'dates': dates,
            'full_df': {
                'close': close_df,
                'high': high_df,
                'low': low_df,
                'open': open_df,
                'volume': volume_df
            }
        }
    
    def get_sample_data(
        self,
        symbols: List[str],
        start_date: str,
        end_date: str,
        limit: int = None
    ) -> List[Dict[str, Any]]:
        """
        Get stock data for frontend display
        
        Args:
            symbols: List of stock symbols
            start_date: Start date
            end_date: End date
            limit: Maximum rows per symbol (None for all data)
        
        Returns:
            List of price records
        """
        stocks = self.db.get_stocks_by_symbols(symbols)
        if not stocks:
            return []
        
        symbol_to_id = {stock['symbol']: stock['id'] for stock in stocks}
        stock_ids = [stock['id'] for stock in stocks]
        
        prices = self.db.get_multiple_stock_prices(stock_ids, start_date, end_date)
        
        logger.info(f"Fetched {len(prices)} price records for {len(symbols)} symbols")
        
        # Convert to list of dicts with symbol
        result = []
        max_records = limit * len(symbols) if limit else len(prices)
        for price in prices[:max_records]:
            stock_id = price['stock_id']
            symbol = next((s for s, sid in symbol_to_id.items() if sid == stock_id), None)
            if symbol:
                result.append({
                    'symbol': symbol,
                    'date': price['date'].strftime('%Y-%m-%d'),
                    'open': float(price['open']),
                    'high': float(price['high']),
                    'low': float(price['low']),
                    'close': float(price['close']),
                    'volume': int(price['volume'])
                })
        
        return result


# Global instance
data_service = DataService()

