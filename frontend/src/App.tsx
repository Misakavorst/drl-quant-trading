import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Layout } from 'antd'
import AppLayout from './components/Layout/AppLayout'
import StockManagement from './pages/StockManagement'
import AgentTraining from './pages/AgentTraining'
import Backtesting from './pages/Backtesting'

const { Content } = Layout

function App() {
  return (
    <Router>
      <AppLayout>
        <Content style={{ padding: '24px', minHeight: 'calc(100vh - 64px)' }}>
          <Routes>
            <Route path="/" element={<StockManagement />} />
            <Route path="/training" element={<AgentTraining />} />
            <Route path="/backtesting" element={<Backtesting />} />
          </Routes>
        </Content>
      </AppLayout>
    </Router>
  )
}

export default App

