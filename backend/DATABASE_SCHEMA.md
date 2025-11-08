# Database Schema Documentation

## Database Information

- **Database**: `fin_ai_world_model_v2`
- **Schema**: `kol`
- **Connection**: SSH Tunnel to `kv.run:10022`

## Tables

### `kol.stock`

Stock information table.

**Columns**:
- `id` (integer) - Primary key
- `ticker` (varchar) - Stock ticker symbol (e.g., 'AAPL', 'MSFT')
- `name` (varchar) - Company name

**Example**:
```sql
SELECT id, ticker, name FROM kol.stock WHERE ticker = 'AAPL';
```

### `kol.stock_price`

Historical stock price data.

**Columns**:
- `id` (integer) - Primary key
- `stock_id` (integer) - Foreign key to `kol.stock.id`
- `date` (date) - Trading date
- `open_price` (double precision) - Opening price
- `high_price` (double precision) - High price
- `low_price` (double precision) - Low price
- `close_price` (double precision) - Closing price
- `volume` (integer) - Trading volume

**Example**:
```sql
SELECT stock_id, date, open_price, high_price, low_price, close_price, volume
FROM kol.stock_price
WHERE stock_id = 1 AND date BETWEEN '2024-01-01' AND '2024-12-31'
ORDER BY date;
```

## Field Mappings in Code

The backend code uses simplified field names for consistency with the frontend:

### Stock Table Mapping:
- `ticker` → `symbol` (aliased in queries)
- Other fields kept as-is

### Stock Price Table Mapping:
- `open_price` → `open`
- `high_price` → `high`
- `low_price` → `low`
- `close_price` → `close`
- `volume` → `volume` (unchanged)

## Database Queries Used

### Get Stock by Symbol
```python
query = "SELECT id, ticker as symbol, name FROM kol.stock WHERE ticker = %s LIMIT 1"
```

### Get Multiple Stocks
```python
query = "SELECT id, ticker as symbol, name FROM kol.stock WHERE ticker IN (%s, %s, ...)"
```

### Get Stock Prices
```python
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
```

### Get Multiple Stock Prices
```python
query = """
    SELECT id, stock_id, date,
           open_price as open, high_price as high,
           low_price as low, close_price as close, volume
    FROM kol.stock_price 
    WHERE stock_id IN (%s, %s, ...)
    AND date >= %s 
    AND date <= %s
    ORDER BY date ASC, stock_id ASC
"""
```

## Important Notes

1. **Schema Prefix Required**: All queries must use `kol.` prefix for table names
2. **Field Name Mapping**: The code automatically maps database field names to simplified names
3. **Date Format**: Dates should be in 'YYYY-MM-DD' format
4. **Ticker Symbols**: Use the actual ticker symbols from the database (case-sensitive)

## Testing Database Connection

Run the test script to verify connection and data:

```bash
cd backend
python test_db.py
```

Expected output:
- SSH tunnel connection successful
- Schema inspection shows correct columns
- Sample stocks listed
- Price data retrieved for date range

## Troubleshooting

### "relation does not exist" error
- **Cause**: Missing `kol.` schema prefix
- **Fix**: All table references must use `kol.stock` and `kol.stock_price`

### "column does not exist" error
- **Cause**: Using simplified field names instead of actual database columns
- **Fix**: Use `ticker` instead of `symbol`, `open_price` instead of `open`, etc.

### No data returned
- **Cause**: Invalid date range or non-existent ticker symbols
- **Fix**: Check actual data availability with test script

## Data Availability

To check what data is available:

```sql
-- Get list of available stocks
SELECT ticker, name FROM kol.stock ORDER BY ticker;

-- Get date range for a stock
SELECT MIN(date) as min_date, MAX(date) as max_date 
FROM kol.stock_price 
WHERE stock_id = 1;

-- Count records per stock
SELECT s.ticker, COUNT(*) as record_count
FROM kol.stock_price sp
JOIN kol.stock s ON sp.stock_id = s.id
GROUP BY s.ticker
ORDER BY record_count DESC;
```

