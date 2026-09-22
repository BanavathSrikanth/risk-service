import React, { useState } from 'react';
import { DollarSign, TrendingUp, AlertCircle, ArrowRight, CheckCircle2 } from 'lucide-react';

export default function FinancialEngine({ bffUrl }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const [formData, setFormData] = useState({
    asset_id: 'POLE-88421',
    tenant_id: 'PACIFIC-POWER',
    condition_band: 'POOR',
    replacement_cost: 150000,
    customers: 4500,
    outage_hours: 24,
    outage_cost_per_customer_hour: 18,
    wildfire_liability_exposure: 6000000,
    hftd_tier: 'Tier3',
    action_cost: 38000,
    remaining_life: 2.5,
    design_life: 40,
    discount_rate: 0.07,
    degradation_rate: 0.05,
  });

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) || 0 : value,
    }));
  };

  const handleEvaluate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${bffUrl}/bff/api/v1/evaluate-financials`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errText = await response.text();
        throw new Error(`BFF Financial API error (${response.status}): ${errText}`);
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
    <div className="grid-2col">
      {/* Form Input Panel */}
      <div className="glass-panel" style={{ padding: '1.75rem' }}>
        <div className="form-title">
          <DollarSign style={{ color: 'var(--accent-emerald)' }} size={24} />
          Financial Exposure & ROI Parameters
        </div>

        <form onSubmit={handleEvaluate}>
          <div className="form-group-grid">
            <div className="field-box">
              <label className="field-label">Asset ID</label>
              <input type="text" name="asset_id" className="field-input" value={formData.asset_id} onChange={handleChange} required />
            </div>
            <div className="field-box">
              <label className="field-label">Condition Band</label>
              <select name="condition_band" className="field-select" value={formData.condition_band} onChange={handleChange}>
                <option value="CRITICAL">Critical</option>
                <option value="POOR">Poor</option>
                <option value="FAIR">Fair</option>
                <option value="GOOD">Good</option>
              </select>
            </div>
          </div>

          <div style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--accent-emerald)', marginBottom: '0.75rem', textTransform: 'uppercase', marginTop: '0.5rem' }}>
            Capital & Exposure Costs
          </div>
          <div className="form-group-grid">
            <div className="field-box">
              <label className="field-label">Replacement Cost ($)</label>
              <input type="number" name="replacement_cost" className="field-input" value={formData.replacement_cost} onChange={handleChange} />
            </div>
            <div className="field-box">
              <label className="field-label">Mitigation Cost ($)</label>
              <input type="number" name="action_cost" className="field-input" value={formData.action_cost} onChange={handleChange} />
            </div>
            <div className="field-box">
              <label className="field-label">Customer Count</label>
              <input type="number" name="customers" className="field-input" value={formData.customers} onChange={handleChange} />
            </div>
            <div className="field-box">
              <label className="field-label">Outage Duration (Hours)</label>
              <input type="number" name="outage_hours" className="field-input" value={formData.outage_hours} onChange={handleChange} />
            </div>
          </div>

          <div style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--accent-amber)', marginBottom: '0.75rem', textTransform: 'uppercase', marginTop: '0.5rem' }}>
            Wildfire & Risk Parameters
          </div>
          <div className="form-group-grid">
            <div className="field-box">
              <label className="field-label">Wildfire Exposure ($)</label>
              <input type="number" name="wildfire_liability_exposure" className="field-input" value={formData.wildfire_liability_exposure} onChange={handleChange} />
            </div>
            <div className="field-box">
              <label className="field-label">HFTD Tier</label>
              <select name="hftd_tier" className="field-select" value={formData.hftd_tier} onChange={handleChange}>
                <option value="Tier3">Tier 3 (Extreme)</option>
                <option value="Tier2">Tier 2 (Elevated)</option>
                <option value="NonHFTD">Non-HFTD</option>
              </select>
            </div>
            <div className="field-box">
              <label className="field-label">Discount Rate (0-1)</label>
              <input type="number" step="0.01" name="discount_rate" className="field-input" value={formData.discount_rate} onChange={handleChange} />
            </div>
          </div>

          <button type="submit" className="btn-primary" disabled={loading} style={{ marginTop: '1rem', background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)', boxShadow: '0 4px 20px rgba(16, 185, 129, 0.4)' }}>
            {loading ? (
              <>
                <div className="spinner" /> Evaluating Financial Model...
              </>
            ) : (
              <>
                <TrendingUp size={18} /> Evaluate Financial Impact
              </>
            )}
          </button>
        </form>

        {error && (
          <div style={{ marginTop: '1.25rem', padding: '1rem', background: 'rgba(244, 63, 94, 0.15)', border: '1px solid rgba(244, 63, 94, 0.3)', borderRadius: '10px', color: '#fca5a5', fontSize: '0.9rem' }}>
            <AlertCircle size={18} style={{ marginRight: '0.5rem', verticalAlign: 'middle' }} />
            {error}
          </div>
        )}
      </div>

      {/* Results Projection Panel */}
      <div className="glass-panel" style={{ padding: '1.75rem' }}>
        <div className="form-title">
          <TrendingUp style={{ color: 'var(--accent-emerald)' }} size={24} />
          Projected Financial Engine Output
        </div>

        {result ? (
          <div>
            {/* Metric Cards Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
              <div style={{ padding: '1.1rem', background: 'rgba(16, 185, 129, 0.12)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '12px', textAlign: 'center' }}>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#6ee7b7', textTransform: 'uppercase' }}>Net Benefit</div>
                <div style={{ fontFamily: 'var(--font-heading)', fontSize: '1.5rem', fontWeight: 800, color: '#34d399', marginTop: '0.2rem' }}>
                  {result.formatted_net_benefit}
                </div>
              </div>

              <div style={{ padding: '1.1rem', background: 'rgba(6, 182, 212, 0.12)', border: '1px solid rgba(6, 182, 212, 0.3)', borderRadius: '12px', textAlign: 'center' }}>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#67e8f9', textTransform: 'uppercase' }}>Project ROI</div>
                <div style={{ fontFamily: 'var(--font-heading)', fontSize: '1.5rem', fontWeight: 800, color: '#22d3ee', marginTop: '0.2rem' }}>
                  {result.formatted_roi}
                </div>
              </div>

              <div style={{ padding: '1.1rem', background: 'rgba(245, 158, 11, 0.12)', border: '1px solid rgba(245, 158, 11, 0.3)', borderRadius: '12px', textAlign: 'center' }}>
                <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#fcd34d', textTransform: 'uppercase' }}>Annual Loss (EAL)</div>
                <div style={{ fontFamily: 'var(--font-heading)', fontSize: '1.5rem', fontWeight: 800, color: '#fbbf24', marginTop: '0.2rem' }}>
                  {result.formatted_eal}
                </div>
              </div>
            </div>

            {/* Recommendation Box */}
            <div className="recommendation-box" style={{ borderLeftColor: '#10b981', marginBottom: '1.5rem' }}>
              <strong style={{ color: '#34d399' }}>BFF Capital Recommendation:</strong>
              <p style={{ marginTop: '0.25rem' }}>{result.investment_recommendation}</p>
            </div>

            {/* Scenario Matrix Table */}
            {result.scenarios && (
              <div>
                <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#e2e8f0', marginBottom: '0.75rem' }}>
                  Scenario Sensitivity Analysis
                </div>
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-muted)' }}>
                        <th style={{ padding: '0.6rem', textAlign: 'left' }}>Scenario</th>
                        <th style={{ padding: '0.6rem', textAlign: 'right' }}>P(Fail)</th>
                        <th style={{ padding: '0.6rem', textAlign: 'right' }}>Consequence</th>
                        <th style={{ padding: '0.6rem', textAlign: 'right' }}>Avoided Loss</th>
                        <th style={{ padding: '0.6rem', textAlign: 'right' }}>ROI</th>
                      </tr>
                    </thead>
                    <tbody>
                      {['low', 'base', 'high'].map((scKey) => {
                        const sc = result.scenarios[scKey];
                        if (!sc) return null;
                        return (
                          <tr key={scKey} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)', color: scKey === 'base' ? '#ffffff' : 'var(--text-muted)' }}>
                            <td style={{ padding: '0.65rem', fontWeight: scKey === 'base' ? 700 : 400, textTransform: 'capitalize' }}>
                              {scKey} Scenario
                            </td>
                            <td style={{ padding: '0.65rem', textAlign: 'right' }}>{(sc.failure_probability * 100).toFixed(1)}%</td>
                            <td style={{ padding: '0.65rem', textAlign: 'right' }}>${(sc.consequence / 1000).toFixed(0)}k</td>
                            <td style={{ padding: '0.65rem', textAlign: 'right' }}>${(sc.avoided_loss / 1000).toFixed(0)}k</td>
                            <td style={{ padding: '0.65rem', textAlign: 'right', fontWeight: 700, color: sc.roi > 0 ? '#34d399' : '#f87171' }}>
                              {(sc.roi * 100).toFixed(1)}%
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '320px', color: 'var(--text-dim)', textAlign: 'center' }}>
            <ArrowRight size={48} style={{ marginBottom: '1rem', opacity: 0.4 }} />
            <p>Click "Evaluate Financial Impact" to trigger BFF financial modeling.</p>
            <span style={{ fontSize: '0.8rem', marginTop: '0.5rem' }}>
              Frontend (React) ➔ BFF (Port 8001) ➔ Financial Engine (Port 8000)
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
