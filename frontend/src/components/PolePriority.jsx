import React, { useState } from 'react';
import { ListOrdered, AlertTriangle, ArrowRight, ShieldCheck } from 'lucide-react';

export default function PolePriority({ bffUrl }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const [formData, setFormData] = useState({
    asset_id: 'POLE-88421',
    tenant_id: 'PACIFIC-POWER',
    composite_risk_score: 84.5,
    consequence_score: 78.0,
    hazard_exposure_score: 88.0,
    days_overdue: 55,
    inspection_confidence: 0.9,
  });

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) || 0 : value,
    }));
  };

  const handlePrioritize = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${bffUrl}/bff/api/v1/pole-priority`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errText = await response.text();
        throw new Error(`BFF Priority API error (${response.status}): ${errText}`);
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
          <ListOrdered style={{ color: 'var(--accent-amber)' }} size={24} />
          Pole Work Order Prioritization Queue
        </div>

        <form onSubmit={handlePrioritize}>
          <div className="form-group-grid">
            <div className="field-box">
              <label className="field-label">Asset ID</label>
              <input type="text" name="asset_id" className="field-input" value={formData.asset_id} onChange={handleChange} required />
            </div>
            <div className="field-box">
              <label className="field-label">Tenant ID</label>
              <input type="text" name="tenant_id" className="field-input" value={formData.tenant_id} onChange={handleChange} required />
            </div>
          </div>

          <div style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--accent-amber)', marginBottom: '0.75rem', textTransform: 'uppercase', marginTop: '0.5rem' }}>
            Queue Scoring Factors
          </div>
          <div className="form-group-grid">
            <div className="field-box">
              <label className="field-label">Composite Risk Score (0-100)</label>
              <input type="number" name="composite_risk_score" className="field-input" value={formData.composite_risk_score} onChange={handleChange} />
            </div>
            <div className="field-box">
              <label className="field-label">Consequence Score (0-100)</label>
              <input type="number" name="consequence_score" className="field-input" value={formData.consequence_score} onChange={handleChange} />
            </div>
            <div className="field-box">
              <label className="field-label">Hazard Exposure Score (0-100)</label>
              <input type="number" name="hazard_exposure_score" className="field-input" value={formData.hazard_exposure_score} onChange={handleChange} />
            </div>
            <div className="field-box">
              <label className="field-label">Days Overdue</label>
              <input type="number" name="days_overdue" className="field-input" value={formData.days_overdue} onChange={handleChange} />
            </div>
            <div className="field-box">
              <label className="field-label">Inspection Confidence (0-1)</label>
              <input type="number" step="0.05" name="inspection_confidence" className="field-input" value={formData.inspection_confidence} onChange={handleChange} />
            </div>
          </div>

          <button type="submit" className="btn-primary" disabled={loading} style={{ marginTop: '1rem', background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)', boxShadow: '0 4px 20px rgba(245, 158, 11, 0.4)' }}>
            {loading ? (
              <>
                <div className="spinner" /> Calculating Priority...
              </>
            ) : (
              <>
                <ListOrdered size={18} /> Calculate Priority Queue Score
              </>
            )}
          </button>
        </form>

        {error && (
          <div style={{ marginTop: '1.25rem', padding: '1rem', background: 'rgba(244, 63, 94, 0.15)', border: '1px solid rgba(244, 63, 94, 0.3)', borderRadius: '10px', color: '#fca5a5', fontSize: '0.9rem' }}>
            <AlertTriangle size={18} style={{ marginRight: '0.5rem', verticalAlign: 'middle' }} />
            {error}
          </div>
        )}
      </div>

      {/* Output Results Panel */}
      <div className="glass-panel" style={{ padding: '1.75rem' }}>
        <div className="form-title">
          <ShieldCheck style={{ color: result ? result.priority_color : 'var(--text-muted)' }} size={24} />
          Projected Priority Queue Output
        </div>

        {result ? (
          <div>
            {/* Score Hero Dial */}
            <div className="score-hero">
              <div className="badge-tag" style={{ background: `${result.priority_color}25`, border: `1px solid ${result.priority_color}`, color: result.priority_color }}>
                {result.priority_tier}
              </div>
              <div className="score-circle" style={{ borderColor: result.priority_color, boxShadow: `0 0 30px ${result.priority_color}50` }}>
                <span className="score-num" style={{ color: result.priority_color }}>{result.priority_score}</span>
                <span className="score-max">QUEUE INDEX</span>
              </div>
            </div>

            {/* Recommendation Box */}
            <div className="recommendation-box" style={{ borderLeftColor: result.priority_color, marginBottom: '1.5rem' }}>
              <strong style={{ color: result.priority_color }}>BFF Dispatch Guidance:</strong>
              <p style={{ marginTop: '0.25rem' }}>{result.urgency_recommendation}</p>
            </div>

            {/* Breakdown Grid */}
            {result.score_breakdown && (
              <div>
                <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#e2e8f0', marginBottom: '0.5rem' }}>
                  Queue Score Component Breakdown
                </div>
                <div className="factor-grid">
                  {Object.entries(result.score_breakdown).map(([k, v]) => (
                    <div className="factor-card" key={k}>
                      <div className="factor-name">{k.replace('_', ' ').toUpperCase()}</div>
                      <div className="factor-val">{typeof v === 'number' ? v.toFixed(1) : v}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '320px', color: 'var(--text-dim)', textAlign: 'center' }}>
            <ArrowRight size={48} style={{ marginBottom: '1rem', opacity: 0.4 }} />
            <p>Click "Calculate Priority Queue Score" to trigger BFF priority scoring.</p>
            <span style={{ fontSize: '0.8rem', marginTop: '0.5rem' }}>
              Frontend (React) ➔ BFF (Port 8001) ➔ Pole Priority API (Port 8000)
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
