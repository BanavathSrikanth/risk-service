import React, { useState } from 'react';
import { Layers, Activity, ShieldAlert, DollarSign, ListOrdered, CheckCircle2, AlertTriangle, ArrowRight } from 'lucide-react';

export default function UnifiedAuditDashboard({ bffUrl }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [assetId, setAssetId] = useState('POLE-88421');
  const [tenantId, setTenantId] = useState('PACIFIC-POWER');

  const handleRunAudit = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${bffUrl}/bff/api/v1/asset-risk-summary`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ asset_id: assetId, tenant_id: tenantId }),
      });

      if (!response.ok) {
        const errText = await response.text();
        throw new Error(`BFF Audit error (${response.status}): ${errText}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {/* Top Banner Control */}
      <div className="glass-panel" style={{ padding: '1.5rem 2rem', marginBottom: '1.75rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.4rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <Layers style={{ color: 'var(--primary)' }} size={24} />
            Unified BFF Single-Click Asset Audit
          </h2>
          <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
            One frontend click triggers BFF orchestration across Risk, Financial Engine, Priority, and History microservices.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <input
              type="text"
              className="field-input"
              value={assetId}
              onChange={(e) => setAssetId(e.target.value)}
              placeholder="Asset ID"
              style={{ width: '140px' }}
            />
            <input
              type="text"
              className="field-input"
              value={tenantId}
              onChange={(e) => setTenantId(e.target.value)}
              placeholder="Tenant ID"
              style={{ width: '150px' }}
            />
          </div>

          <button onClick={handleRunAudit} className="btn-primary" disabled={loading} style={{ width: 'auto', padding: '0.75rem 1.5rem' }}>
            {loading ? (
              <>
                <div className="spinner" /> Orchestrating BFF Audit...
              </>
            ) : (
              <>
                <Activity size={18} /> Run Comprehensive Audit
              </>
            )}
          </button>
        </div>
      </div>

      {error && (
        <div style={{ marginBottom: '1.5rem', padding: '1rem', background: 'rgba(244, 63, 94, 0.15)', border: '1px solid rgba(244, 63, 94, 0.3)', borderRadius: '10px', color: '#fca5a5', fontSize: '0.9rem' }}>
          <AlertTriangle size={18} style={{ marginRight: '0.5rem', verticalAlign: 'middle' }} />
          {error}
        </div>
      )}

      {/* Projection View */}
      {result ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Status Header */}
          <div className="glass-panel" style={{ padding: '1.25rem 1.75rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: 'linear-gradient(135deg, rgba(17,24,39,0.9) 0%, rgba(30,41,59,0.9) 100%)' }}>
            <div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Asset Identifier: <strong>{result.asset_id}</strong> | Tenant: <strong>{result.tenant_id}</strong>
              </div>
              <div style={{ fontFamily: 'var(--font-heading)', fontSize: '1.6rem', fontWeight: 800, color: '#ffffff', marginTop: '0.25rem' }}>
                Overall Asset Status: <span style={{ color: result.overall_health_status.includes('CRITICAL') ? '#f87171' : '#34d399' }}>{result.overall_health_status}</span>
              </div>
            </div>

            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>History Evaluation Records</div>
              <div style={{ fontFamily: 'var(--font-heading)', fontSize: '1.5rem', fontWeight: 700, color: 'var(--accent-cyan)' }}>
                {result.history_count} Logged Audit(s)
              </div>
            </div>
          </div>

          {/* 3-Column Aggregated Results Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem' }}>
            {/* Risk Card */}
            {result.risk && (
              <div className="glass-panel" style={{ padding: '1.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                  <span style={{ fontSize: '0.9rem', fontWeight: 700, color: '#ffffff', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <ShieldAlert style={{ color: result.risk.category_color }} size={18} /> Risk Score
                  </span>
                  <span className="badge-tag" style={{ background: `${result.risk.category_color}25`, border: `1px solid ${result.risk.category_color}`, color: result.risk.category_color, fontSize: '0.72rem' }}>
                    {result.risk.risk_category}
                  </span>
                </div>

                <div style={{ textAlign: 'center', margin: '1rem 0' }}>
                  <div style={{ fontFamily: 'var(--font-heading)', fontSize: '3rem', fontWeight: 800, color: result.risk.category_color, lineHeight: 1 }}>
                    {result.risk.risk_score}
                  </div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Score (0 - 100)</span>
                </div>

                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>
                  {result.risk.action_recommendation}
                </p>
              </div>
            )}

            {/* Financial Card */}
            {result.financials && (
              <div className="glass-panel" style={{ padding: '1.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                  <span style={{ fontSize: '0.9rem', fontWeight: 700, color: '#ffffff', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <DollarSign style={{ color: 'var(--accent-emerald)' }} size={18} /> Financial Model
                  </span>
                  <span className="badge-tag" style={{ background: 'rgba(16,185,129,0.2)', border: '1px solid #10b981', color: '#34d399', fontSize: '0.72rem' }}>
                    ROI {result.financials.formatted_roi}
                  </span>
                </div>

                <div style={{ margin: '1rem 0', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Net Benefit:</span>
                    <strong style={{ color: '#34d399' }}>{result.financials.formatted_net_benefit}</strong>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Annual Loss (EAL):</span>
                    <strong style={{ color: '#fbbf24' }}>{result.financials.formatted_eal}</strong>
                  </div>
                </div>

                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>
                  {result.financials.investment_recommendation}
                </p>
              </div>
            )}

            {/* Priority Card */}
            {result.priority && (
              <div className="glass-panel" style={{ padding: '1.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
                  <span style={{ fontSize: '0.9rem', fontWeight: 700, color: '#ffffff', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <ListOrdered style={{ color: result.priority.priority_color }} size={18} /> Work Priority
                  </span>
                  <span className="badge-tag" style={{ background: `${result.priority.priority_color}25`, border: `1px solid ${result.priority.priority_color}`, color: result.priority.priority_color, fontSize: '0.72rem' }}>
                    {result.priority.priority_tier.split(' - ')[0]}
                  </span>
                </div>

                <div style={{ textAlign: 'center', margin: '1rem 0' }}>
                  <div style={{ fontFamily: 'var(--font-heading)', fontSize: '3rem', fontWeight: 800, color: result.priority.priority_color, lineHeight: 1 }}>
                    {result.priority.priority_score}
                  </div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Queue Score Index</span>
                </div>

                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.4 }}>
                  {result.priority.urgency_recommendation}
                </p>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="glass-panel" style={{ padding: '4rem 2rem', textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
          <Activity size={56} style={{ color: 'var(--primary)', marginBottom: '1.25rem', opacity: 0.8 }} />
          <h3 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.3rem', fontWeight: 700, marginBottom: '0.5rem' }}>
            Single-Click BFF Unified Orchestration
          </h3>
          <p style={{ color: 'var(--text-muted)', maxWidth: '500px', fontSize: '0.95rem', lineHeight: 1.5 }}>
            Click <strong>"Run Comprehensive Audit"</strong> above to observe how the BFF aggregates backend risk models, financial evaluations, and priority algorithms into a unified dashboard view.
          </p>
        </div>
      )}
    </div>
  );
}
