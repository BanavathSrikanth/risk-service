import React, { useState } from 'react';
import { ShieldAlert, Zap, AlertTriangle, CheckCircle2, ArrowRight } from 'lucide-react';

export default function RiskCalculator({ bffUrl }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const [formData, setFormData] = useState({
    asset_id: 'POLE-88421',
    tenant_id: 'PACIFIC-POWER',
    age_years: 28,
    material: 'wood',
    remaining_fiber_pct: 60,
    defect_severity: 'major',
    lean_deg: 6,
    attachment_count: 5,
    asset_class: 'distribution',
    reinforced_within_10_years: false,
    population_exposure: 80,
    critical_infrastructure: 65,
    service_impact: 75,
    failure_cost: 550000,
    outage_duration_hours: 36,
    customer_count: 4200,
    wind_speed_mph: 48,
    temperature_f: 102,
    relative_humidity_pct: 14,
    precipitation_in: 0,
    fire_weather_index: 85,
    days_overdue: 60,
    work_already_scheduled: false,
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : type === 'number' ? parseFloat(value) || 0 : value,
    }));
  };

  const handleCalculate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${bffUrl}/bff/api/v1/calculate-risk`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errText = await response.text();
        throw new Error(`BFF Server returned ${response.status}: ${errText}`);
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
      {/* Input Form Panel */}
      <div className="glass-panel" style={{ padding: '1.75rem' }}>
        <div className="form-title">
          <Zap style={{ color: 'var(--primary)' }} size={24} />
          Asset Risk Assessment Input
        </div>

        <form onSubmit={handleCalculate}>
          <div className="form-group-grid">
            <div className="field-box">
              <label className="field-label">Asset ID</label>
              <input
                type="text"
                name="asset_id"
                className="field-input"
                value={formData.asset_id}
                onChange={handleChange}
                required
              />
            </div>
            <div className="field-box">
              <label className="field-label">Tenant ID</label>
              <input
                type="text"
                name="tenant_id"
                className="field-input"
                value={formData.tenant_id}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--accent-cyan)', marginBottom: '0.75rem', textTransform: 'uppercase' }}>
            Structural & Asset Factors (AHS)
          </div>
          <div className="form-group-grid">
            <div className="field-box">
              <label className="field-label">Age (Years)</label>
              <input type="number" name="age_years" className="field-input" value={formData.age_years} onChange={handleChange} />
            </div>
            <div className="field-box">
              <label className="field-label">Material</label>
              <select name="material" className="field-select" value={formData.material} onChange={handleChange}>
                <option value="wood">Wood</option>
                <option value="steel">Steel</option>
                <option value="concrete">Concrete</option>
                <option value="composite">Composite</option>
              </select>
            </div>
            <div className="field-box">
              <label className="field-label">Remaining Fiber %</label>
              <input type="number" name="remaining_fiber_pct" className="field-input" value={formData.remaining_fiber_pct} onChange={handleChange} />
            </div>
            <div className="field-box">
              <label className="field-label">Defect Severity</label>
              <select name="defect_severity" className="field-select" value={formData.defect_severity} onChange={handleChange}>
                <option value="none">None</option>
                <option value="minor">Minor</option>
                <option value="moderate">Moderate</option>
                <option value="major">Major</option>
                <option value="critical">Critical</option>
              </select>
            </div>
            <div className="field-box">
              <label className="field-label">Lean (Degrees)</label>
              <input type="number" name="lean_deg" className="field-input" value={formData.lean_deg} onChange={handleChange} />
            </div>
          </div>

          <div style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--accent-amber)', marginBottom: '0.75rem', textTransform: 'uppercase', marginTop: '0.5rem' }}>
            Consequence & Hazard Exposure (CES & DHM)
          </div>
          <div className="form-group-grid">
            <div className="field-box">
              <label className="field-label">Population Exposure (0-100)</label>
              <input type="number" name="population_exposure" className="field-input" value={formData.population_exposure} onChange={handleChange} />
            </div>
            <div className="field-box">
              <label className="field-label">Wind Speed (MPH)</label>
              <input type="number" name="wind_speed_mph" className="field-input" value={formData.wind_speed_mph} onChange={handleChange} />
            </div>
            <div className="field-box">
              <label className="field-label">Fire Weather Index</label>
              <input type="number" name="fire_weather_index" className="field-input" value={formData.fire_weather_index} onChange={handleChange} />
            </div>
            <div className="field-box">
              <label className="field-label">Days Overdue</label>
              <input type="number" name="days_overdue" className="field-input" value={formData.days_overdue} onChange={handleChange} />
            </div>
          </div>

          <button type="submit" className="btn-primary" disabled={loading} style={{ marginTop: '1rem' }}>
            {loading ? (
              <>
                <div className="spinner" /> Calling BFF & Backend Risk API...
              </>
            ) : (
              <>
                <Zap size={18} /> Calculate Risk Score
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
          <ShieldAlert style={{ color: result ? result.category_color : 'var(--text-muted)' }} size={24} />
          Projected BFF Risk Output
        </div>

        {result ? (
          <div>
            {/* Score Hero Dial */}
            <div className="score-hero">
              <div className="badge-tag" style={{ background: `${result.category_color}25`, border: `1px solid ${result.category_color}`, color: result.category_color }}>
                {result.risk_category} RISK LEVEL
              </div>
              <div className="score-circle" style={{ borderColor: result.category_color, boxShadow: `0 0 30px ${result.category_color}50` }}>
                <span className="score-num" style={{ color: result.category_color }}>{result.risk_score}</span>
                <span className="score-max">/ 100</span>
              </div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                Confidence Score: <strong style={{ color: '#34d399' }}>{(result.confidence * 100).toFixed(0)}%</strong>
              </div>
            </div>

            {/* Recommendation Box */}
            <div className="recommendation-box" style={{ borderLeftColor: result.category_color, marginBottom: '1.5rem' }}>
              <strong style={{ color: result.category_color }}>BFF Recommendation:</strong>
              <p style={{ marginTop: '0.25rem' }}>{result.action_recommendation}</p>
            </div>

            {/* Composite Factor Breakdown Grid */}
            <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#e2e8f0', marginBottom: '0.5rem' }}>
              Composite Risk Factor Breakdown
            </div>
            <div className="factor-grid">
              <div className="factor-card">
                <div className="factor-name">AHS (Condition)</div>
                <div className="factor-val">{result.factor_scores.AHS}</div>
              </div>
              <div className="factor-card">
                <div className="factor-name">CES (Consequence)</div>
                <div className="factor-val">{result.factor_scores.CES}</div>
              </div>
              <div className="factor-card">
                <div className="factor-name">CQS (Exposure)</div>
                <div className="factor-val">{result.factor_scores.CQS}</div>
              </div>
              <div className="factor-card">
                <div className="factor-name">DHM (Hazard)</div>
                <div className="factor-val">{result.factor_scores.DHM}</div>
              </div>
              <div className="factor-card">
                <div className="factor-name">OPS (Operational)</div>
                <div className="factor-val">{result.factor_scores.OPS}</div>
              </div>
              <div className="factor-card">
                <div className="factor-name">VES (Evidence)</div>
                <div className="factor-val">{result.factor_scores.VES}</div>
              </div>
            </div>

            {/* Key Drivers */}
            {result.drivers && result.drivers.length > 0 && (
              <div style={{ marginTop: '1.5rem' }}>
                <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#e2e8f0', marginBottom: '0.5rem' }}>
                  Key Risk Score Drivers
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                  {result.drivers.map((drv, idx) => (
                    <div key={idx} style={{ padding: '0.6rem 0.85rem', background: 'rgba(15,23,42,0.5)', borderRadius: '8px', border: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: '0.9rem', color: '#cbd5e1' }}>Factor: <strong>{drv.factor}</strong></span>
                      <span style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--accent-cyan)' }}>Score: {drv.score}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '320px', color: 'var(--text-dim)', textAlign: 'center' }}>
            <ArrowRight size={48} style={{ marginBottom: '1rem', opacity: 0.4 }} />
            <p>Click "Calculate Risk Score" to trigger the BFF pipeline.</p>
            <span style={{ fontSize: '0.8rem', marginTop: '0.5rem' }}>
              Frontend (React) ➔ BFF (Port 8001) ➔ Service API (Port 8000)
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
