import { useState, useEffect, useCallback } from 'react'
import {
  Card,
  Form,
  Select,
  Button,
  Table,
  Progress,
  Tag,
  Space,
  message,
  Row,
  Col,
  Typography,
  Statistic,
  Divider,
  DatePicker,
  Slider,
  InputNumber,
} from 'antd'
import {
  PlayCircleOutlined,
  ReloadOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  CopyOutlined,
} from '@ant-design/icons'
import dayjs, { Dayjs } from 'dayjs'
import { trainingService, TrainingProgress, TrainingResult, TrainingHistoryItem } from '../services/trainingService'
import { stockService, StockOption } from '../services/stockService'
import type { ColumnsType } from 'antd/es/table'

const { Title } = Typography
const { Option } = Select
const { RangePicker } = DatePicker

const AgentTraining = () => {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const [training, setTraining] = useState(false)
  const [jobId, setJobId] = useState<string | null>(null)
  const [progress, setProgress] = useState<TrainingProgress[]>([])
  const [results, setResults] = useState<TrainingResult[]>([])
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null)
  const [history, setHistory] = useState<TrainingHistoryItem[]>([])
  const [showHistory, setShowHistory] = useState(false)
  const [stockOptions, setStockOptions] = useState<StockOption[]>([])
  
  const loadJobProgress = async (id: string) => {
    try {
      const progressData = await trainingService.getProgress(id)
      setProgress(progressData.progress)
      setResults(progressData.results)
    } catch (error) {
      console.error('Failed to load job progress:', error)
    }
  }

  const loadHistory = async () => {
    try {
      const historyData = await trainingService.getHistory()
      setHistory(historyData)
      setShowHistory(true)
    } catch (error: any) {
      message.error('Failed to load training history')
    }
  }

  const loadHistoricalJob = async (histJobId: string) => {
    setJobId(histJobId)
    await loadJobProgress(histJobId)
    setShowHistory(false)
    message.success('Loaded historical training job')
  }

  const handleStockSearch = useCallback(async (value: string) => {
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
  
  // Load last job ID on component mount
  useEffect(() => {
    const lastJobId = localStorage.getItem('lastTrainingJobId')
    if (lastJobId && !jobId) {
      setJobId(lastJobId)
      loadJobProgress(lastJobId)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval)
      }
    }
  }, [pollingInterval])

  const startTraining = async (values: {
    symbols: string[]
    algorithms: string[]
    dateRange?: [Dayjs, Dayjs]
    trainTestSplit?: number
    totalTimesteps?: number
  }) => {
    setLoading(true)
    try {
      const response = await trainingService.startTraining({
        symbols: values.symbols,
        algorithms: values.algorithms,
        startDate: values.dateRange ? values.dateRange[0].format('YYYY-MM-DD') : undefined,
        endDate: values.dateRange ? values.dateRange[1].format('YYYY-MM-DD') : undefined,
        trainTestSplit: values.trainTestSplit ? values.trainTestSplit / 100 : undefined,
        totalTimesteps: values.totalTimesteps,
      })

      setJobId(response.jobId)
      setTraining(true)
      message.success(`Training started! Job ID: ${response.jobId}`)
      
      // Store job ID in localStorage for later use
      localStorage.setItem('lastTrainingJobId', response.jobId)
      
      // Start polling for progress
      const interval = setInterval(async () => {
        try {
          const progressData = await trainingService.getProgress(response.jobId)
          setProgress(progressData.progress)
          setResults(progressData.results)

          // Check if all training is completed
          const allCompleted = progressData.progress.every(
            (p) => p.status === 'completed' || p.status === 'failed'
          )
          if (allCompleted) {
            setTraining(false)
            clearInterval(interval)
            setPollingInterval(null)
            message.success('Training completed!')
          }
        } catch (error) {
          console.error('Error fetching progress:', error)
        }
      }, 2000) // Poll every 2 seconds

      setPollingInterval(interval)
    } catch (error: any) {
      message.error(error?.response?.data?.message || 'Failed to start training')
    } finally {
      setLoading(false)
    }
  }

  const progressColumns: ColumnsType<TrainingProgress> = [
    {
      title: 'Algorithm',
      dataIndex: 'algorithm',
      key: 'algorithm',
      width: 120,
      render: (algorithm: string) => <Tag color="blue">{algorithm}</Tag>,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status: string) => {
        const statusConfig: Record<string, { color: string; icon: React.ReactNode }> = {
          pending: { color: 'default', icon: <ReloadOutlined /> },
          training: { color: 'processing', icon: <ReloadOutlined spin /> },
          completed: { color: 'success', icon: <CheckCircleOutlined /> },
          failed: { color: 'error', icon: <CloseCircleOutlined /> },
        }
        const config = statusConfig[status] || statusConfig.pending
        return (
          <Tag color={config.color} icon={config.icon}>
            {status.toUpperCase()}
          </Tag>
        )
      },
    },
    {
      title: 'Progress',
      key: 'progress',
      width: 200,
      render: (_, record: TrainingProgress) => {
        if (record.status === 'pending') {
          return <Progress percent={0} status="active" />
        }
        if (record.status === 'failed') {
          return <Progress percent={0} status="exception" />
        }
        const percent = Math.round(
          (record.epoch / record.totalEpochs) * 100
        )
        return (
          <Progress
            percent={percent}
            status={record.status === 'training' ? 'active' : 'success'}
            format={() => `${record.epoch}/${record.totalEpochs}`}
          />
        )
      },
    },
    {
      title: 'Loss',
      dataIndex: 'loss',
      key: 'loss',
      width: 100,
      render: (loss: number) => (loss ? loss.toFixed(4) : '-'),
    },
    {
      title: 'Reward',
      dataIndex: 'reward',
      key: 'reward',
      width: 100,
      render: (reward: number) => (reward ? reward.toFixed(2) : '-'),
    },
  ]

  const resultsColumns: ColumnsType<TrainingResult> = [
    {
      title: 'Algorithm',
      dataIndex: 'algorithm',
      key: 'algorithm',
      width: 120,
      fixed: 'left',
      render: (text: string, record: TrainingResult) => (
        <Space>
          {record.status === 'completed' ? (
            <CheckCircleOutlined style={{ color: '#52c41a' }} />
          ) : (
            <CloseCircleOutlined style={{ color: '#f5222d' }} />
          )}
          <strong>{text}</strong>
        </Space>
      ),
    },
    {
      title: 'Return Rate',
      dataIndex: ['metrics', 'returnRate'],
      key: 'returnRate',
      width: 120,
      render: (value: number) => (
        <span style={{ color: (value || 0) > 0 ? '#3f8600' : '#cf1322', fontWeight: 'bold' }}>
          {(value || 0).toFixed(2)}%
        </span>
      ),
      sorter: (a, b) => (a.metrics.returnRate || 0) - (b.metrics.returnRate || 0),
      defaultSortOrder: 'descend',
    },
    {
      title: 'Initial Capital',
      dataIndex: ['metrics', 'initialAmount'],
      key: 'initialAmount',
      width: 130,
      render: (value: number) => `$${(value || 0).toLocaleString()}`,
    },
    {
      title: 'Final Value',
      dataIndex: ['metrics', 'finalAmount'],
      key: 'finalAmount',
      width: 130,
      render: (value: number) => `$${(value || 0).toLocaleString()}`,
    },
    {
      title: 'Total Profit',
      key: 'profit',
      width: 130,
      render: (_, record: TrainingResult) => {
        const profit = (record.metrics.finalAmount || 0) - (record.metrics.initialAmount || 0)
        return (
          <span style={{ color: profit > 0 ? '#3f8600' : '#cf1322' }}>
            ${profit.toLocaleString()}
          </span>
        )
      },
    },
    {
      title: 'Sharpe Ratio',
      dataIndex: ['metrics', 'sharpeRatio'],
      key: 'sharpeRatio',
      width: 120,
      render: (value: number) => (value || 0).toFixed(2),
      sorter: (a, b) => (a.metrics.sharpeRatio || 0) - (b.metrics.sharpeRatio || 0),
    },
    {
      title: 'Max Drawdown',
      dataIndex: ['metrics', 'maxDrawdown'],
      key: 'maxDrawdown',
      width: 120,
      render: (value: number) => `${((value || 0) * 100).toFixed(2)}%`,
    },
    {
      title: 'Win Rate',
      dataIndex: ['metrics', 'winRate'],
      key: 'winRate',
      width: 100,
      render: (value: number) => `${((value || 0) * 100).toFixed(2)}%`,
    },
    {
      title: 'Training Time',
      dataIndex: 'trainingTime',
      key: 'trainingTime',
      width: 120,
      render: (value: number) => `${(value || 0).toFixed(2)}s`,
    },
  ]

  const historyColumns: ColumnsType<TrainingHistoryItem> = [
    {
      title: 'Job ID',
      dataIndex: 'jobId',
      key: 'jobId',
      width: 150,
      render: (text: string) => (
        <Tag color="blue" style={{ fontFamily: 'monospace', fontSize: 11 }}>
          {text.slice(0, 8)}...
        </Tag>
      ),
    },
    {
      title: 'Symbols',
      dataIndex: 'symbols',
      key: 'symbols',
      render: (symbols: string[]) => symbols.join(', '),
    },
    {
      title: 'Algorithms',
      dataIndex: 'algorithms',
      key: 'algorithms',
      render: (algorithms: string[]) => algorithms.join(', '),
    },
    {
      title: 'Date Range',
      key: 'dateRange',
      render: (_, record) => (
        record.startDate && record.endDate
          ? `${record.startDate} ~ ${record.endDate}`
          : 'Default'
      ),
    },
    {
      title: 'Created At',
      dataIndex: 'createdAt',
      key: 'createdAt',
      width: 170,
    },
    {
      title: 'Status',
      dataIndex: 'completed',
      key: 'completed',
      width: 100,
      render: (completed: boolean) => (
        <Tag color={completed ? 'success' : 'processing'}>
          {completed ? 'Completed' : 'In Progress'}
        </Tag>
      ),
    },
    {
      title: 'Action',
      key: 'action',
      width: 100,
      render: (_, record) => (
        <Button
          type="link"
          size="small"
          onClick={() => loadHistoricalJob(record.jobId)}
          disabled={!record.completed}
        >
          View
        </Button>
      ),
    },
  ]

  return (
    <div>
      <Space style={{ marginBottom: 16, justifyContent: 'space-between', width: '100%' }}>
        <Title level={2} style={{ margin: 0 }}>Agent Training</Title>
        <Button
          icon={<ReloadOutlined />}
          onClick={loadHistory}
        >
          Training History
        </Button>
      </Space>

      {showHistory && (
        <Card style={{ marginBottom: 24 }}>
          <Space style={{ marginBottom: 16, justifyContent: 'space-between', width: '100%' }}>
            <Title level={4} style={{ margin: 0 }}>Training History</Title>
            <Button onClick={() => setShowHistory(false)}>Close</Button>
          </Space>
          <Table
            columns={historyColumns}
            dataSource={history}
            rowKey="jobId"
            pagination={{ pageSize: 10 }}
          />
        </Card>
      )}

      <Card style={{ marginBottom: 24 }}>
        <Form
          form={form}
          layout="vertical"
          onFinish={startTraining}
          initialValues={{
            algorithms: ['PPO', 'DQN'],
            dateRange: [dayjs().subtract(3, 'year'), dayjs()],
            trainTestSplit: 80,
            totalTimesteps: 10000,
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
                  onSearch={handleStockSearch}
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
                tooltip="Select the date range for training data (optional, defaults to 2020-01-01 to 2023-12-31)"
              >
                <RangePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12} md={8}>
              <Form.Item
                label="DRL Algorithms"
                name="algorithms"
                rules={[
                  { required: true, message: 'Please select algorithms' },
                ]}
              >
                <Select mode="multiple" placeholder="Select algorithms">
                  <Option value="PPO">PPO (Proximal Policy Optimization)</Option>
                  <Option value="DQN">DQN (Deep Q-Network)</Option>
                  <Option value="A2C">A2C (Advantage Actor-Critic)</Option>
                  <Option value="SAC">SAC (Soft Actor-Critic)</Option>
                  <Option value="TD3">TD3 (Twin Delayed DDPG)</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col xs={24} sm={12} md={12}>
              <Form.Item
                label={
                  <span>
                    Train/Test Split: <strong>{form.getFieldValue('trainTestSplit') || 80}%</strong> Train / <strong>{100 - (form.getFieldValue('trainTestSplit') || 80)}%</strong> Test
                  </span>
                }
                name="trainTestSplit"
                tooltip="Percentage of data used for training (remaining is used for testing)"
              >
                <Slider
                  min={50}
                  max={90}
                  step={5}
                  marks={{
                    50: '50%',
                    60: '60%',
                    70: '70%',
                    80: '80%',
                    90: '90%',
                  }}
                />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12} md={12}>
              <Form.Item
                label="Training Timesteps"
                name="totalTimesteps"
                tooltip="Total number of timesteps for training (smaller for quick testing, larger for better results)"
              >
                <InputNumber
                  min={1000}
                  max={100000}
                  step={1000}
                  style={{ width: '100%' }}
                  placeholder="10000"
                  formatter={(value) => `${value}`.replace(/\B(?=(\d{3})+(?!\d))/g, ',')}
                  parser={(value) => value!.replace(/,/g, '')}
                />
              </Form.Item>
            </Col>
            <Col xs={24} sm={24} md={24}>
              <Form.Item label=" ">
                <Button
                  type="primary"
                  htmlType="submit"
                  icon={<PlayCircleOutlined />}
                  loading={loading}
                  disabled={training}
                  size="large"
                  block
                >
                  Start Training
                </Button>
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Card>

      {jobId && (
        <>
          <Card style={{ marginBottom: 24 }}>
            <Space direction="vertical" size="small" style={{ width: '100%', marginBottom: 16 }}>
              <Title level={4} style={{ marginBottom: 0 }}>Training Progress</Title>
              <Space>
                <strong>Job ID:</strong>
                <Tag color="blue" style={{ fontFamily: 'monospace' }}>{jobId}</Tag>
                <Button
                  size="small"
                  icon={<CopyOutlined />}
                  onClick={() => {
                    navigator.clipboard.writeText(jobId)
                    message.success('Job ID copied to clipboard!')
                  }}
                >
                  Copy ID
                </Button>
              </Space>
            </Space>
            <Table
              columns={progressColumns}
              dataSource={progress.map((p, index) => ({ ...p, key: index }))}
              pagination={false}
              size="small"
            />
          </Card>

          {results.length > 0 && (
            <Card>
              <Title level={4}>Training Results</Title>
              <Row gutter={16} style={{ marginBottom: 24 }}>
                {results.map((result) => (
                  <Col xs={24} sm={12} md={6} key={result.algorithm}>
                    <Card>
                      <Space direction="vertical" style={{ width: '100%' }}>
                        <Statistic
                          title={result.algorithm}
                          value={result.metrics.returnRate || 0}
                          precision={2}
                          valueStyle={{
                            color:
                              result.status === 'completed' && (result.metrics.returnRate || 0) > 0
                                ? '#3f8600'
                                : '#cf1322',
                          }}
                          prefix={
                            result.status === 'completed' ? (
                              <CheckCircleOutlined />
                            ) : (
                              <CloseCircleOutlined />
                            )
                          }
                          suffix="%"
                        />
                        <Divider style={{ margin: '8px 0' }} />
                        <div style={{ fontSize: 12, color: '#666' }}>
                          <div><strong>Initial:</strong> ${(result.metrics.initialAmount || 0).toLocaleString()}</div>
                          <div><strong>Final:</strong> ${(result.metrics.finalAmount || 0).toLocaleString()}</div>
                          <div style={{ color: ((result.metrics.finalAmount || 0) - (result.metrics.initialAmount || 0)) > 0 ? '#3f8600' : '#cf1322' }}>
                            <strong>Profit:</strong> ${((result.metrics.finalAmount || 0) - (result.metrics.initialAmount || 0)).toLocaleString()}
                          </div>
                        </div>
                      </Space>
                    </Card>
                  </Col>
                ))}
              </Row>
              <Table
                columns={resultsColumns}
                dataSource={results.map((r, index) => ({ ...r, key: index }))}
                pagination={false}
              />
            </Card>
          )}
        </>
      )}
    </div>
  )
}

export default AgentTraining

