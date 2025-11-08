"""Test database connection and query capabilities"""
import sys
from app.database import db_manager

def test_connection():
    """Test SSH tunnel and database connection"""
    print("=" * 60)
    print("Testing Database Connection")
    print("=" * 60)
    
    try:
        # Start tunnel
        print("\n1. Starting SSH tunnel...")
        db_manager.start_tunnel()
        print(f"   ✓ SSH tunnel started on local port {db_manager.local_port}")
        
        # Inspect schema
        print("\n2. Inspecting database schema...")
        schema = db_manager.inspect_schema()
        
        print(f"   ✓ Stock table has {len(schema['stock'])} columns:")
        for col in schema['stock'][:3]:
            print(f"     - {col['column_name']}: {col['data_type']}")
        
        print(f"   ✓ Stock price table has {len(schema['stock_price'])} columns:")
        for col in schema['stock_price'][:5]:
            print(f"     - {col['column_name']}: {col['data_type']}")
        
        # Test stock query
        print("\n3. Testing stock queries...")
        
        # First check what stocks are available
        sample_query = "SELECT ticker, name FROM kol.stock LIMIT 5"
        sample_stocks = db_manager.execute_query(sample_query)
        print(f"   Sample stocks in database:")
        for s in sample_stocks:
            print(f"     - {s['ticker']}: {s.get('name', 'N/A')}")
        
        # Use actual tickers from database if available
        test_symbols = [s['ticker'] for s in sample_stocks[:3]] if sample_stocks else ['AAPL', 'MSFT', 'GOOGL']
        print(f"\n   Testing with symbols: {test_symbols}")
        
        stocks = db_manager.get_stocks_by_symbols(test_symbols)
        
        if stocks:
            print(f"   ✓ Found {len(stocks)} stocks:")
            for stock in stocks:
                print(f"     - {stock['symbol']}: {stock.get('name', 'N/A')} (ID: {stock['id']})")
            
            # Test price query
            print("\n4. Testing price queries...")
            stock_id = stocks[0]['id']
            
            # Try to find what date range has data
            date_range_query = f"""
                SELECT MIN(date) as min_date, MAX(date) as max_date 
                FROM kol.stock_price 
                WHERE stock_id = {stock_id}
            """
            date_range = db_manager.execute_query(date_range_query)
            if date_range and date_range[0]['min_date']:
                min_date = date_range[0]['min_date']
                max_date = date_range[0]['max_date']
                print(f"   Available data range: {min_date} to {max_date}")
                
                # Use the actual date range
                prices = db_manager.get_stock_prices(
                    stock_id=stock_id,
                    start_date=str(min_date),
                    end_date=str(max_date)
                )
                
                if prices:
                    print(f"   ✓ Found {len(prices)} price records for {stocks[0]['symbol']}")
                    print(f"     First record: {prices[0]['date']} - Close: ${prices[0]['close']:.2f}")
                    print(f"     Last record: {prices[-1]['date']} - Close: ${prices[-1]['close']:.2f}")
                else:
                    print("   ⚠ No price data found")
            else:
                print("   ⚠ No price data available for this stock")
        else:
            print(f"   ⚠ No stocks found for symbols: {test_symbols}")
            print("   This might be expected if database uses different symbols")
        
        print("\n" + "=" * 60)
        print("✓ All tests completed successfully!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Cleanup
        print("\n5. Cleaning up...")
        db_manager.stop_tunnel()
        print("   ✓ SSH tunnel stopped")


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)

