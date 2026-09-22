# InfraIQ Asset Intelligence API

FastAPI service for assets, inspections, financial exposure, GIS, and risk calculation. The HTTP contract is OpenAPI at `/docs` and `/openapi.json`, so React, .NET, and other clients can generate typed clients without importing Python code.

## Run locally

```powershell
cd infraiq_risklayer/apps/services/risk-service
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:PYTHONPATH = (Get-Location).Path
uvicorn app.api.main:app --reload
```

Open `http://localhost:8000/docs`.

## Run with Docker

```powershell
copy .env.example .env
docker compose up --build
```

Azure Blob Storage is enabled when `BLOB_CONNECTION_STRING` is set. Redis is enabled through `REDIS_URL`. Azure AI Foundry settings are reserved in `FOUNDRY_ENDPOINT` and `FOUNDRY_API_KEY`; no credential is committed to the repository.

## Financial engine

`POST /api/v1/financial-engine/evaluate` calculates low/base/high scenarios for
failure probability, consequence, expected annual loss, discounted cost of
inaction, residual value destroyed, avoided loss, net benefit, ROI, and
break-even year. SME-editable illustrative USD assumptions are loaded from
`app/domain/rules/v1/financial.yaml`, validated, and identified by
`calculation_version`. Request values override YAML defaults, while omitted
financial assumptions are filled from the YAML file. A new YAML version never
changes an existing evaluation.

Each result stores an `assumption_version` and a complete `inputs_snapshot`.
`GET /api/v1/financial-engine/history/{asset_id}?tenant_id=...` returns the
append-only evaluation history for that tenant and asset. Durable SQLAlchemy/Alembic persistence is provided under
`app/infrastructure/persistence`. Run `alembic upgrade head` from this service
directory after setting `sqlalchemy.url` (or `DATABASE_URL` in your deployment
configuration). Repositories require an explicit tenant id for every query and
keep risk history append-only.

The deterministic formulas are:

```text
P_fail = failure_rate[condition_band] * (1 + CES / 100) * scenario_multiplier
consequence = replacement_cost
              + customers * outage_hours * outage_cost_per_customer_hour
              + ignition_probability[hftd_tier] * wildfire_liability_exposure
EAL = P_fail * consequence
PV(risk) = sum(P_fail * (1 + degradation_rate)^(year - 1)
               * consequence / (1 + discount_rate)^year)
avoided_loss = PV(current condition) - PV(post-action condition)
residual_value_destroyed = replacement_cost
                            * remaining_life / design_life
net_benefit = avoided_loss - action_cost - residual_value_destroyed
ROI = net_benefit / action_cost
```

The YAML contains the failure rates, HFTD ignition probabilities, cost bands,
outage assumptions, discount/degradation rates, scenario multipliers,
design-life assumptions, and wildfire liability exposure. These are sample
SME-editable values, not universal platform defaults; production tenants should
approve and version their own assumption set.

## API resources

- `POST/GET /api/v1/assets`: asset master data and lifecycle state.
- `POST/GET /api/v1/inspections`: inspection observations and evidence metadata.
- `POST/GET /api/v1/financials`: replacement, outage, operating, and customer exposure.
- `PUT/GET /api/v1/gis/assets/{asset_id}`: asset coordinates.
- `GET /api/v1/gis/map-config`: MapLibre style and OSM tile configuration.
- `GET /api/v1/gis/geocode?query=...`: OSM Nominatim geocoding.
- `POST /api/v1/inspections/{inspection_id}/evidence`: upload raw inspection evidence to Blob Storage; send the filename in `X-File-Name` and the MIME type in `Content-Type`.
- `POST /api/v1/risks/calculate`: calculate a versioned risk result.
- `GET /api/v1/risks/latest/{asset_id}`: read the cached result when Redis is configured.
- `GET /api/v1/risks/history/{asset_id}`: read append-only risk evaluations.
- `POST /api/v1/risks/pole-priority`: calculate a versioned pole work-priority score; this does not authorize replacement or assign work.

Every resource carries `tenant_id`; production authentication should derive that value from a validated token rather than trusting arbitrary client input.

## Formula governance

The v1.1 composite formula includes VES as a weighted risk factor:

`risk_score = AHS * w_ahs + CES * w_ces + CQS * w_cqs + DHM * w_dhm + OPS * w_ops + VES * w_ves`

The weights and thresholds are versioned in `app/domain/rules/v1/*.yaml`. The v1.1 composite weights sum to `1.0`; SME changes must update the YAML and receive regression tests.

`VES = AHS * w_asset_condition + CES * w_consequence + exposure * w_exposure + severity * w_severity + evidence_factor * 100 * w_evidence`

OPS uses the v1.1 operational-priority formula:

`base = 0.40 * AHS + 0.25 * CES + 0.35 * CQS`

`DHM = clamp(base, 1.0, 2.5)`

`OPS = clamp(base * DHM + min(15, (days_overdue / 30) * 5) - (10 if work_already_scheduled else 0), 0, 100)`

When a contributing feed is stale, its request value must be the last known
value and the result is marked `stale=true`; stale values are never replaced
with a default score.

Confidence is calculated independently from the score as the product across
the required AHS, CES, CQS, DHM, and VES feeds: `1.0` for present and fresh,
`0.8` for present but beyond SLA, `0.5` for distribution-imputed, and `0.3`
for missing. A missing critical input caps confidence at `0.5` and adds a
visible warning. Confidence never reduces the calculated risk score.
When dataset columns are omitted, the result also identifies the exact
nested columns, such as `weather.wind_speed_mph` or `cqs.failure_cost`.

Do not put formula constants in routes or frontend code. A rule change creates a new rule version and should receive new regression tests.

## Spatial hazard and pole priority

The geospatial service provides timestamped hazard exposures from live heat,
flood, wind, fire, and related polygon layers. The risk API consumes those
exposures as immutable inputs. Pole prioritization is a separate, versioned
queue calculation combining risk, hazard exposure, consequence, urgency, and
inspection confidence. Its result is advisory for routing and planning; an
authorized decision is still required for consequential work such as pole
replacement.

## Column mapping

| Source column | API field | Domain meaning | Unit / constraints |
|---|---|---|---|
| `asset_id` | `AssetCreate.asset_id` | Stable asset identifier | Non-empty string |
| `tenant_id` | `*.tenant_id` | Customer or organizational boundary | Non-empty string |
| `asset_class` | `AssetCreate.asset_class` / `RiskInput.ahs.asset_class` | Distribution or transmission class | String matching configured rules |
| `material` | `AssetCreate.material` / `RiskInput.ahs.material` | Physical material | Rule key such as `wood`, `steel`, `concrete` |
| `inspection_date` | `InspectionCreate.inspected_at` | Observation time | ISO-8601 UTC datetime |
| `defect_severity` | `InspectionCreate.defect_severity` / `RiskInput.ahs.defect_severity` | Defect severity category | `none`, `minor`, `moderate`, `major`, `critical` |
| `condition_score` | `InspectionCreate.condition_score` | Normalized inspection condition | 0-100 |
| `population_exposure` | `RiskInput.consequence.population_exposure` | Population exposure consequence | 0-100 |
| `critical_infrastructure` | `RiskInput.consequence.critical_infrastructure` | Critical infrastructure consequence | 0-100 |
| `service_impact` | `RiskInput.consequence.service_impact` | Service disruption consequence | 0-100 |
| `failure_cost` | `RiskInput.cqs.failure_cost` | Financial consequence of failure | Account currency |
| `outage_duration_hours` | `RiskInput.cqs.outage_duration_hours` | Expected outage duration | Hours, non-negative |
| `customer_count` | `RiskInput.cqs.customer_count` / `FinancialCreate.customer_count` | Customers affected | Non-negative integer |
| `latitude` / `longitude` | `AssetCreate.latitude` / `AssetCreate.longitude` | Asset location | WGS84 degrees |
| `replacement_cost` | `FinancialCreate.replacement_cost` | Replacement exposure | Account currency |
| `currency` | `FinancialCreate.currency` | Financial currency | ISO-4217 code |
| `evidence_blob_name` | `InspectionCreate.evidence_blob_name` | Blob reference | Blob name, never raw secret |

For .NET, generate a client from `/openapi.json` with NSwag or Kiota. For React, generate TypeScript types or use the same OpenAPI document with Orval; send ISO-8601 dates and preserve numeric fields as numbers.
