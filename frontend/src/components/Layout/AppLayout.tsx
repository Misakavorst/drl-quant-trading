import { Layout, Menu } from 'antd'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  StockOutlined,
  RobotOutlined,
  LineChartOutlined,
} from '@ant-design/icons'
import type { ReactNode } from 'react'

const { Header, Sider } = Layout

interface AppLayoutProps {
  children: ReactNode
}

const AppLayout = ({ children }: AppLayoutProps) => {
  const navigate = useNavigate()
  const location = useLocation()

  const menuItems = [
    {
      key: '/',
      icon: <StockOutlined />,
      label: 'Stock Management',
    },
    {
      key: '/training',
      icon: <RobotOutlined />,
      label: 'Agent Training',
    },
    {
      key: '/backtesting',
      icon: <LineChartOutlined />,
      label: 'Backtesting',
    },
  ]

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header
        style={{
          background: '#001529',
          padding: '0 24px',
          display: 'flex',
          alignItems: 'center',
        }}
      >
        <div
          style={{
            color: '#fff',
            fontSize: '20px',
            fontWeight: 'bold',
            marginRight: '24px',
          }}
        >
          DRL Quantitative Trading Analysis
        </div>
      </Header>
      <Layout>
        <Sider
          width={200}
          style={{
            background: '#fff',
            borderRight: '1px solid #f0f0f0',
          }}
        >
          <Menu
            mode="inline"
            selectedKeys={[location.pathname]}
            style={{ height: '100%', borderRight: 0 }}
            items={menuItems}
            onClick={({ key }) => navigate(key)}
          />
        </Sider>
        <Layout style={{ background: '#f0f2f5' }}>
          {children}
        </Layout>
      </Layout>
    </Layout>
  )
}

export default AppLayout

