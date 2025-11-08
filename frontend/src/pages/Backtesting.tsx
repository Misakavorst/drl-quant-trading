import { useState, useEffect } from 'react'
import {
  Card,
  Form,
  Select,
  Input,
  Button,
  Table,
  Tag,
  Space,
  message,
  Row,
  Col,
  Typography,
  Statistic,
  Divider,
  Radio,
} from 'antd'
import {
  PlayCircleOutlined,
  ReloadOutlined,
  LineChartOutlined,
} from '@ant-design/icons'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  BarChart,
  Bar,
} from 'recharts'
import {
  backtestingService,
  BacktestResult,
} from '../services/backtestingService'
import type { ColumnsType } from 'antd/es/table'

const { Title } = Typography
const { Option } = Select

const Backtesting = () => {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [backtesting, setBacktesting] = useState(false)
  const [jobId, setJobId] = useState<string | null>(null)
  const [results, setResults] = useState<BacktestResult[]>([])
  const [comparison, setComparison] = useState<any>(null)
  const [chartType, setChartType] = useState<'cumulative' | 'returns' | 'metrics'>('cumulative')
  
  // Load last training job ID on component mount
  useEffect(() => {
    const lastJobId = localStorage.getItem('lastTrainingJobId')
    if (lastJobId) {
      form.setFieldsValue({ trainingJobId: lastJobId })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const startBacktest = async (values: {
    trainingJobId: string
    baselineStrategies?: string[]
  }) => {
    setLoading(true)
    setBacktesting(false)
    
    try {
      const response = await backtestingService.startBacktest({
        jobId: values.trainingJobId,
        baselineStrategies: values.baselineStrategies || [],
      })

      setJobId(response.jobId)
      setLoading(false)  // Stop button loading
      setBacktesting(true)  // Start backtesting indicator
      message.success('Backtesting started successfully')

      // Poll for results
      const pollResults = async () => {
        try {
          const backtestResults = await backtestingService.getResults(response.jobId)
          setResults(backtestResults.results)
          setComparison(backtestResults.comparison)
          setBacktesting(false)
          message.success('Backtesting completed!')
        } catch (error: any) {
          if (error?.response?.status === 404) {
            // Results not ready yet, keep polling
            setTimeout(pollResults, 2000)
          } else {
            // Other error, stop polling
            setBacktesting(false)
            message.error('Backtesting failed: ' + (error?.response?.data?.detail || error.message))
          }
        }
      }

      // Start polling after a short delay
      setTimeout(pollResults, 2000)
    } catch (error: any) {
      message.error(error?.response?.data?.detail || error?.response?.data?.message || 'Failed to start backtesting')
      setLoading(false)
      setBacktesting(false)
    }
  }

  // Prepare chart data
  const prepareCumulativeReturnsData = () => {
    if (results.length === 0) return []

    // Get all unique dates
    const allDates = new Set<string>()
    results.forEach((result) => {
      result.dates.forEach((date) => allDates.add(date))
    })

    const sortedDates = Array.from(allDates).sort()

    // Create data points for each date
    const chartData = sortedDates.map((date) => {
      const dataPoint: any = { date }
      results.forEach((result) => {
        const index = result.dates.indexOf(date)
        if (index !== -1) {
          dataPoint[result.algorithm] = result.cumulativeReturns[index]
        }
      })
      return dataPoint
    })

    return chartData
  }

  const prepareReturnsData = () => {
    if (results.length === 0) return []

    const allDates = new Set<string>()
    results.forEach((result) => {
      result.dates.forEach((date) => allDates.add(date))
    })

    const sortedDates = Array.from(allDates).sort()

    const chartData = sortedDates.map((date) => {
      const dataPoint: any = { date }
      results.forEach((result) => {
        const index = result.dates.indexOf(date)
        if (index !== -1) {
          dataPoint[result.algorithm] = result.returns[index]
        }
      })
      return dataPoint
    })

    return chartData
  }

  const prepareMetricsData = () => {
    return results.map((result) => ({
      algorithm: result.algorithm,
      totalReturn: result.metrics.totalReturn,
      sharpeRatio: result.metrics.sharpeRatio,
      maxDrawdown: result.metrics.maxDrawdown,
      volatility: result.metrics.volatility,
      winRate: result.metrics.winRate * 100,
    }))
  }

  const getColorForAlgorithm = (algorithm: string, index: number) => {
    const colors = [
      '#1890ff',
      '#52c41a',
      '#faad14',
      '#f5222d',
      '#722ed1',
      '#13c2c2',
      '#eb2f96',
    ]
    return colors[index % colors.length]
  }

  const resultsColumns: ColumnsType<BacktestResult> = [
    {
      title: 'Algorithm',
      dataIndex: 'algorithm',
      key: 'algorithm',
      width: 150,
      render: (algorithm: string, record: BacktestResult) => (
        <Space>
          <Tag color={record.type === 'drl' ? 'blue' : 'green'}>
            {record.type.toUpperCase()}
          </Tag>
          <strong>{algorithm}</strong>
        </Space>
      ),
    },
    {
      title: 'Total Return',
      dataIndex: ['metrics', 'totalReturn'],
      key: 'totalReturn',
      width: 120,
      render: (value: number) => (
        <span style={{ color: value > 0 ? '#3f8600' : '#cf1322' }}>
          {value > 0 ? '+' : ''}
          {(value * 100).toFixed(2)}%
        </span>
      ),
      sorter: (a, b) => a.metrics.totalReturn - b.metrics.totalReturn,
    },
    {
      title: 'Sharpe Ratio',
      dataIndex: ['metrics', 'sharpeRatio'],
      key: 'sharpeRatio',
      width: 120,
      render: (value: number) => value.toFixed(4),
      sorter: (a, b) => a.metrics.sharpeRatio - b.metrics.sharpeRatio,
    },
    {
      title: 'Max Drawdown',
      dataIndex: ['metrics', 'maxDrawdown'],
      key: 'maxDrawdown',
      width: 120,
      render: (value: number) => (
        <span style={{ color: '#cf1322' }}>{value.toFixed(2)}%</span>
      ),
      sorter: (a, b) => a.metrics.maxDrawdown - b.metrics.maxDrawdown,
    },
    {
      title: 'Volatility',
      dataIndex: ['metrics', 'volatility'],
      key: 'volatility',
      width: 120,
      render: (value: number) => `${(value * 100).toFixed(2)}%`,
      sorter: (a, b) => a.metrics.volatility - b.metrics.volatility,
    },
    {
      title: 'Win Rate',
      dataIndex: ['metrics', 'winRate'],
      key: 'winRate',
      width: 100,
      render: (value: number) => `${(value * 100).toFixed(2)}%`,
      sorter: (a, b) => a.metrics.winRate - b.metrics.winRate,
    },
  ]

  return (
    <div>
      <Title level={2}>Backtesting</Title>
      <Card style={{ marginBottom: 24 }}>
        <Form
          form={form}
          layout="vertical"
          onFinish={startBacktest}
          initialValues={{
            baselineStrategies: ['BuyAndHold', 'MovingAverage'],
          }}
        >
          <Row gutter={16}>
            <Col xs={24} sm={12} md={12}>
              <Form.Item
                label="Training Job ID"
                name="trainingJobId"
                rules={[
                  { required: true, message: 'Please enter training job ID' },
                ]}
                tooltip="The Job ID from your training session will be automatically filled. Stocks and date range will be used from the training configuration."
              >
                <Input
                  placeholder="Job ID will be auto-filled from training"
                  style={{ fontFamily: 'monospace' }}
                />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12} md={12}>
              <Form.Item
                label="Baseline Strategies"
                name="baselineStrategies"
                tooltip="Select baseline strategies for comparison"
              >
                <Select mode="multiple" placeholder="Select strategies">
                  <Option value="BuyAndHold">Buy and Hold</Option>
                  <Option value="MovingAverage">Moving Average</Option>
                  <Option value="Random">Random Strategy</Option>
                  <Option value="EqualWeight">Equal Weight</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col xs={24} sm={24} md={24}>
              <Form.Item label=" ">
                <Button
                  type="primary"
                  htmlType="submit"
                  icon={<PlayCircleOutlined />}
                  loading={loading || backtesting}
                  size="large"
                  block
                >
                  {backtesting ? 'Backtesting...' : 'Start Backtesting'}
                </Button>
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Card>

      {results.length > 0 && (
        <>
          {comparison && (
            <Card style={{ marginBottom: 24 }}>
              <Title level={4}>Comparison Summary</Title>
              <Row gutter={16}>
                <Col xs={24} sm={8}>
                  <Statistic
                    title="Best Algorithm"
                    value={comparison.bestAlgorithm}
                    prefix={<LineChartOutlined />}
                  />
                </Col>
                <Col xs={24} sm={8}>
                  <Statistic
                    title="Best Return"
                    value={comparison.bestReturn * 100}
                    precision={2}
                    suffix="%"
                    valueStyle={{ color: '#3f8600' }}
                  />
                </Col>
                <Col xs={24} sm={8}>
                  <Statistic
                    title="Best Sharpe Ratio"
                    value={comparison.bestSharpeRatio}
                    precision={4}
                  />
                </Col>
              </Row>
            </Card>
          )}

          <Card style={{ marginBottom: 24 }}>
            <Space style={{ marginBottom: 16 }}>
              <Title level={4} style={{ margin: 0 }}>
                Charts
              </Title>
              <Radio.Group
                value={chartType}
                onChange={(e) => setChartType(e.target.value)}
                buttonStyle="solid"
              >
                <Radio.Button value="cumulative">Cumulative Returns</Radio.Button>
                <Radio.Button value="returns">Daily Returns</Radio.Button>
                <Radio.Button value="metrics">Metrics Comparison</Radio.Button>
              </Radio.Group>
            </Space>

            {chartType === 'cumulative' && (
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={prepareCumulativeReturnsData()}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="date"
                    tick={{ fontSize: 12 }}
                    angle={-45}
                    textAnchor="end"
                    height={80}
                  />
                  <YAxis
                    tick={{ fontSize: 12 }}
                    label={{ value: 'Cumulative Return', angle: -90, position: 'insideLeft' }}
                  />
                  <Tooltip />
                  <Legend />
                  {results.map((result, index) => (
                    <Line
                      key={result.algorithm}
                      type="monotone"
                      dataKey={result.algorithm}
                      stroke={getColorForAlgorithm(result.algorithm, index)}
                      strokeWidth={2}
                      dot={false}
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            )}

            {chartType === 'returns' && (
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={prepareReturnsData()}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="date"
                    tick={{ fontSize: 12 }}
                    angle={-45}
                    textAnchor="end"
                    height={80}
                  />
                  <YAxis
                    tick={{ fontSize: 12 }}
                    label={{ value: 'Daily Return (%)', angle: -90, position: 'insideLeft' }}
                  />
                  <Tooltip />
                  <Legend />
                  {results.map((result, index) => (
                    <Line
                      key={result.algorithm}
                      type="monotone"
                      dataKey={result.algorithm}
                      stroke={getColorForAlgorithm(result.algorithm, index)}
                      strokeWidth={1.5}
                      dot={false}
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            )}

            {chartType === 'metrics' && (
              <Row gutter={16}>
                <Col xs={24} sm={12}>
                  <Card title="Total Return Comparison" size="small">
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={prepareMetricsData()}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="algorithm" tick={{ fontSize: 10 }} />
                        <YAxis tick={{ fontSize: 10 }} />
                        <Tooltip />
                        <Bar dataKey="totalReturn" fill="#1890ff" />
                      </BarChart>
                    </ResponsiveContainer>
                  </Card>
                </Col>
                <Col xs={24} sm={12}>
                  <Card title="Sharpe Ratio Comparison" size="small">
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={prepareMetricsData()}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="algorithm" tick={{ fontSize: 10 }} />
                        <YAxis tick={{ fontSize: 10 }} />
                        <Tooltip />
                        <Bar dataKey="sharpeRatio" fill="#52c41a" />
                      </BarChart>
                    </ResponsiveContainer>
                  </Card>
                </Col>
                <Col xs={24} sm={12}>
                  <Card title="Max Drawdown Comparison" size="small">
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={prepareMetricsData()}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="algorithm" tick={{ fontSize: 10 }} />
                        <YAxis tick={{ fontSize: 10 }} />
                        <Tooltip />
                        <Bar dataKey="maxDrawdown" fill="#f5222d" />
                      </BarChart>
                    </ResponsiveContainer>
                  </Card>
                </Col>
                <Col xs={24} sm={12}>
                  <Card title="Win Rate Comparison" size="small">
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={prepareMetricsData()}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="algorithm" tick={{ fontSize: 10 }} />
                        <YAxis tick={{ fontSize: 10 }} />
                        <Tooltip />
                        <Bar dataKey="winRate" fill="#faad14" />
                      </BarChart>
                    </ResponsiveContainer>
                  </Card>
                </Col>
              </Row>
            )}
          </Card>

          <Card>
            <Title level={4}>Detailed Results</Title>
            <Table
              columns={resultsColumns}
              dataSource={results.map((r, index) => ({ ...r, key: index }))}
              pagination={false}
              scroll={{ x: 800 }}
            />
          </Card>
        </>
      )}
    </div>
  )
}

export default Backtesting

