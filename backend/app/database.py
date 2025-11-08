"""Database connection and SSH tunnel management"""
import psycopg2
from psycopg2.extras import RealDictCursor
from sshtunnel import SSHTunnelForwarder
from typing import Optional, List, Dict, Any
import logging
from contextlib import contextmanager

from .config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SSH tunnel and PostgreSQL connection"""
    
    def __init__(self):
        self.tunnel: Optional[SSHTunnelForwarder] = None
        self.local_port: Optional[int] = None
        
    def start_tunnel(self):
        """Start SSH tunnel"""
        if self.tunnel and self.tunnel.is_active:
            logger.info("SSH tunnel already active")
            return
            
        try:
            self.tunnel = SSHTunnelForwarder(
                (settings.ssh_host, settings.ssh_port),
                ssh_username=settings.ssh_user,
                ssh_password=settings.ssh_password,
                remote_bind_address=(settings.db_host, settings.db_port),
                local_bind_address=('127.0.0.1', 0)  # Use random available port
            )
            self.tunnel.start()
            self.local_port = self.tunnel.local_bind_port
            logger.info(f"SSH tunnel started on local port {self.local_port}")
        except Exception as e:
            logger.error(f"Failed to start SSH tunnel: {e}")
            raise
    
    def stop_tunnel(self):
        """Stop SSH tunnel"""
        if self.tunnel and self.tunnel.is_active:
            self.tunnel.stop()
            logger.info("SSH tunnel stopped")
            self.tunnel = None
            self.local_port = None
    
    @contextmanager
    def get_connection(self):
        """Get database connection as context manager"""
        if not self.tunnel or not self.tunnel.is_active:
            self.start_tunnel()
        
        conn = None
        try:
            conn = psycopg2.connect(
                host='127.0.0.1',
                port=self.local_port,
                database=settings.db_name,
                user=settings.db_user,
                password=settings.db_password,
                cursor_factory=RealDictCursor
            )
            yield conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                return [dict(row) for row in results]
    
    def get_stock_by_symbol(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get stock information by ticker symbol"""
        query = "SELECT id, ticker as symbol, name FROM kol.stock WHERE ticker = %s LIMIT 1"
        results = self.execute_query(query, (symbol,))
        return results[0] if results else None
    
    def get_stocks_by_symbols(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """Get multiple stocks by ticker symbols"""
        if not symbols:
            return []
        placeholders = ','.join(['%s'] * len(symbols))
        query = f"SELECT id, ticker as symbol, name FROM kol.stock WHERE ticker IN ({placeholders})"
        return self.execute_query(query, tuple(symbols))
    
    def get_stock_prices(
        self, 
        stock_id: int, 
        start_date: str, 
        end_date: str
    ) -> List[Dict[str, Any]]:
        """Get stock prices for a stock within date range"""
        query = """
            SELECT id, stock_id, date,
                   open_price as open, high_price as high,
                   low_price as low, close_price as close, volume
            FROM kol.stock_price 
            WHERE stock_id = %s 
            AND date >= %s 
            AND date <= %s
            ORDER BY date ASC
        """
        return self.execute_query(query, (stock_id, start_date, end_date))
    
    def get_multiple_stock_prices(
        self,
        stock_ids: List[int],
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """Get stock prices for multiple stocks within date range"""
        if not stock_ids:
            return []
        placeholders = ','.join(['%s'] * len(stock_ids))
        query = f"""
            SELECT id, stock_id, date,
                   open_price as open, high_price as high,
                   low_price as low, close_price as close, volume
            FROM kol.stock_price 
            WHERE stock_id IN ({placeholders})
            AND date >= %s 
            AND date <= %s
            ORDER BY date ASC, stock_id ASC
        """
        params = tuple(stock_ids) + (start_date, end_date)
        return self.execute_query(query, params)
    
    def inspect_schema(self) -> Dict[str, Any]:
        """Inspect database schema for stock and stock_price tables"""
        stock_schema = self.execute_query("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'kol' AND table_name = 'stock'
            ORDER BY ordinal_position
        """)
        
        stock_price_schema = self.execute_query("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'kol' AND table_name = 'stock_price'
            ORDER BY ordinal_position
        """)
        
        return {
            "stock": stock_schema,
            "stock_price": stock_price_schema
        }


# Global database manager instance
db_manager = DatabaseManager()

