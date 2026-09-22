import React, { useState, useEffect } from 'react';
import { ShieldCheck, Zap, DollarSign, ListOrdered, Layers, Server, Activity } from 'lucide-react';
import RiskCalculator from './components/RiskCalculator';
import FinancialEngine from './components/FinancialEngine';
import PolePriority from './components/PolePriority';
import UnifiedAuditDashboard from './components/UnifiedAuditDashboard';

const BFF_URL = 'http://localhost:8001';

export default function App() {
  const [activeTab, setActiveTab] = useState('risk');
  const [bffStatus, setBffStatus] = useState({ online: false, backendStatus: 'checking' });

  useEffect(() => {
    const checkBff = async () => {
      try {
        const res = await fetch(`${BFF_URL}/bff/health`, { cache: 'no-store' });
        if (res.ok) {
          const data = await res.json();
          setBffStatus({ online: true, backendStatus: data.backend_status });
        } else {
          setBffStatus({ online: false, backendStatus: 'error' });
        }
      } catch (err) {
        setBffStatus({ online: false, backendStatus: 'offline' });
      }
    };

    checkBff();
    const interval = setInterval(checkBff, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      {/* Top Header */}
      <header className="header-container">
        <div className="logo-group">
          <div className="logo-badge">⚡</div>
          <div>
            <div className="logo-text">InfraIQ Risk Portal</div>
            <span className="bff-badge">BFF Architecture v1.0</span>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div className="status-badge" style={{ borderColor: bffStatus.online ? 'rgba(16, 185, 129, 0.4)' : 'rgba(244, 63, 94, 0.4)', background: bffStatus.online ? 'rgba(16, 185, 129, 0.1)' : 'rgba(244, 63, 94, 0.1)', color: bffStatus.online ? '#34d399' : '#fca5a5' }}>
            <span className="pulse-dot" style={{ backgroundColor: bffStatus.online ? '#10b981' : '#f43f5e', boxShadow: bffStatus.online ? '0 0 10px #10b981' : '0 0 10px #f43f5e' }} />
            {bffStatus.online ? `BFF Online (Port 8001) | Backend: ${bffStatus.backendStatus}` : 'BFF Server Disconnected'}
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="nav-tabs">
        <button className={`tab-btn ${activeTab === 'risk' ? 'active' : ''}`} onClick={() => setActiveTab('risk')}>
          <Zap size={18} /> Asset Risk Calculator
        </button>
        <button className={`tab-btn ${activeTab === 'financial' ? 'active' : ''}`} onClick={() => setActiveTab('financial')}>
          <DollarSign size={18} /> Financial Engine
        </button>
        <button className={`tab-btn ${activeTab === 'priority' ? 'active' : ''}`} onClick={() => setActiveTab('priority')}>
          <ListOrdered size={18} /> Pole Work Priority
        </button>
        <button className={`tab-btn ${activeTab === 'audit' ? 'active' : ''}`} onClick={() => setActiveTab('audit')}>
          <Layers size={18} /> Unified BFF Audit
        </button>
      </nav>

      {/* Main Content Area */}
      <main className="main-container">
        {activeTab === 'risk' && <RiskCalculator bffUrl={BFF_URL} />}
        {activeTab === 'financial' && <FinancialEngine bffUrl={BFF_URL} />}
        {activeTab === 'priority' && <PolePriority bffUrl={BFF_URL} />}
        {activeTab === 'audit' && <UnifiedAuditDashboard bffUrl={BFF_URL} />}
      </main>
    </div>
  );
}
