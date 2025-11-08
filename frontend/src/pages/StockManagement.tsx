import { useState, useCallback } from 'react'
import {
  Card,
  Form,
  Select,
  Button,
  DatePicker,
  Table,
  Tag,
  Space,
  message,
  Row,
  Col,
  Typography,
  Tabs,
  AutoComplete,
} from 'antd'
import { SearchOutlined, StockOutlined, LineChartOutlined, TableOutlined } from '@ant-design/icons'
import dayjs, { Dayjs } from 'dayjs'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { stockService, StockData, StockOption } from '../services/stockService'
import type { ColumnsType } from 'antd/es/table'

const { RangePicker } = DatePicker
const { Title } = Typography
const { TabPane } = Tabs

const StockManagement = () => {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [stockData, setStockData] = useState<StockData[]>([])
  const [selectedSymbols, setSelectedSymbols] = useState<string[]>([])
  const [dateRange, setDateRange] = useState<[Dayjs, Dayjs] | null>(null)
  const [stockOptions, setStockOptions] = useState<StockOption[]>([])
  const [searchValue, setSearchValue] = useState<string>('')

  const handleSearch = useCallback(async (value: string) => {
    if (value.length < 1) {
      setStockOptions([])
      return
    }
    
    try {
      const options = await stockService.getStockList(value)
      setStockOptions(options)
    } catch (error) {
      console.error('Error searching stocks:', error)
    }
  }, [])

  const handleLoadStocks = async (values: {
    symbols: string[]
    dateRange: [Dayjs, Dayjs]
  }) => {
    const symbols = values.symbols
      .map((s) => s.trim().toUpperCase())
      .filter((s) => s.length > 0)

    if (symbols.length === 0) {
      message.error('Please enter at least one stock symbol')
      return
    }

    setLoading(true)
    try {
      const response = await stockService.addStocks({
        symbols,
        startDate: values.dateRange[0].format('YYYY-MM-DD'),
        endDate: values.dateRange[1].format('YYYY-MM-DD'),
      })

      setStockData(response.data)
      setSelectedSymbols(response.symbols)
      setDateRange(values.dateRange)
      message.success(`Successfully loaded ${response.data.length} records for ${response.symbols.length} stock(s)`)
    } catch (error: any) {
      message.error(error?.response?.data?.message || 'Failed to load stocks')
    } finally {
      setLoading(false)
    }
  }

  // Prepare chart data
  const getChartData = () => {
    if (stockData.length === 0) return []
    
    // Group by date
    const dataByDate: Record<string, any> = {}
    stockData.forEach((item) => {
      if (!dataByDate[item.date]) {
        dataByDate[item.date] = { date: item.date }
      }
      dataByDate[item.date][item.symbol] = item.close
    })
    
    return Object.values(dataByDate).sort((a: any, b: any) => 
      a.date.localeCompare(b.date)
    )
  }

  const chartData = getChartData()
  
  // Color palette for chart lines
  const colors = ['#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1', '#13c2c2']

  const columns: ColumnsType<StockData> = [
    {
      title: 'Symbol',
      dataIndex: 'symbol',
      key: 'symbol',
      width: 100,
      render: (symbol: string) => <Tag color="blue">{symbol}</Tag>,
    },
    {
      title: 'Date',
      dataIndex: 'date',
      key: 'date',
      width: 120,
    },
    {
      title: 'Open',
      dataIndex: 'open',
      key: 'open',
      width: 100,
      render: (value: number) => value.toFixed(2),
    },
    {
      title: 'High',
      dataIndex: 'high',
      key: 'high',
      width: 100,
      render: (value: number) => value.toFixed(2),
    },
    {
      title: 'Low',
      dataIndex: 'low',
      key: 'low',
      width: 100,
      render: (value: number) => value.toFixed(2),
    },
    {
      title: 'Close',
      dataIndex: 'close',
      key: 'close',
      width: 100,
      render: (value: number) => <strong>{value.toFixed(2)}</strong>,
    },
    {
      title: 'Volume',
      dataIndex: 'volume',
      key: 'volume',
      width: 120,
      render: (value: number) => value.toLocaleString(),
    },
  ]

  return (
    <div>
      <Title level={2}>Stock Management</Title>
      <Card style={{ marginBottom: 24 }}>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleLoadStocks}
          initialValues={{
            dateRange: [dayjs().subtract(1, 'year'), dayjs()],
          }}
        >
          <Row gutter={16}>
            <Col xs={24} sm={12} md={8}>
              <Form.Item
                label="Stock Symbols"
                name="symbols"
                rules={[
                  { required: true, message: 'Please enter stock symbols' },
                ]}
                tooltip="Type to search and select stocks (e.g., AAPL, MSFT, GOOGL)"
              >
                <Select
                  mode="tags"
                  placeholder="Type to search stocks..."
                  tokenSeparators={[',',' ']}
                  style={{ width: '100%' }}
                  onSearch={handleSearch}
                  filterOption={false}
                  notFoundContent={null}
                  options={stockOptions}
                />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12} md={8}>
              <Form.Item
                label="Date Range"
                name="dateRange"
                rules={[
                  { required: true, message: 'Please select date range' },
                ]}
              >
                <RangePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col xs={24} sm={24} md={8}>
              <Form.Item label=" " style={{ marginTop: 30 }}>
                <Button
                  type="primary"
                  htmlType="submit"
                  icon={<SearchOutlined />}
                  loading={loading}
                  size="large"
                  block
                >
                  Load Stock Data
                </Button>
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Card>

      {selectedSymbols.length > 0 && (
        <Card>
          <Space style={{ marginBottom: 16 }}>
            <strong>Selected Stocks:</strong>
            {selectedSymbols.map((symbol) => (
              <Tag key={symbol} color="blue">
                {symbol}
              </Tag>
            ))}
            {dateRange && (
              <Tag color="green">
                {dateRange[0].format('YYYY-MM-DD')} to{' '}
                {dateRange[1].format('YYYY-MM-DD')}
              </Tag>
            )}
            <Tag color="purple">Total: {stockData.length} records</Tag>
          </Space>
          
          <Tabs defaultActiveKey="chart">
            <TabPane 
              tab={
                <span>
                  <LineChartOutlined />
                  Price Chart
                </span>
              } 
              key="chart"
            >
              {chartData.length > 0 && (
                <ResponsiveContainer width="100%" height={400}>
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="date" 
                      angle={-45}
                      textAnchor="end"
                      height={80}
                      tick={{ fontSize: 12 }}
                      interval={Math.floor(chartData.length / 10)}
                    />
                    <YAxis 
                      label={{ value: 'Price ($)', angle: -90, position: 'insideLeft' }}
                    />
                    <Tooltip />
                    <Legend />
                    {selectedSymbols.map((symbol, index) => (
                      <Line
                        key={symbol}
                        type="monotone"
                        dataKey={symbol}
                        stroke={colors[index % colors.length]}
                        dot={false}
                        strokeWidth={2}
                        name={symbol}
                      />
                    ))}
                  </LineChart>
                </ResponsiveContainer>
              )}
            </TabPane>
            
            <TabPane 
              tab={
                <span>
                  <TableOutlined />
                  Data Table
                </span>
              } 
              key="table"
            >
              <Table
                columns={columns}
                dataSource={stockData.map((item, index) => ({
                  ...item,
                  key: `${item.symbol}-${item.date}-${index}`,
                }))}
                loading={loading}
                pagination={{
                  pageSize: 50,
                  showSizeChanger: true,
                  pageSizeOptions: ['50', '100', '200', '500'],
                  showTotal: (total) => `Total ${total} records`,
                }}
                scroll={{ x: 800 }}
              />
            </TabPane>
          </Tabs>
        </Card>
      )}
    </div>
  )
}

export default StockManagement

