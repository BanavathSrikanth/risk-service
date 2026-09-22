"""create risk, financial, source and vegetation persistence tables"""

from alembic import op
import sqlalchemy as sa

revision = "0001_persistence_foundation"
down_revision = None
branch_labels = None
depends_on = None


def _common(table):
    op.create_index(f"ix_{table}_tenant_id", table, ["tenant_id"])


def upgrade() -> None:
    # Keep JSON payloads flexible while numeric scores and timestamps remain queryable.
    op.create_table(
        "risk_evaluations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(128), nullable=False),
        sa.Column("asset_id", sa.String(128), nullable=False),
        sa.Column("risk_score", sa.Numeric(8, 4), nullable=False),
        sa.Column("risk_category", sa.String(64), nullable=False),
        sa.Column("factor_scores", sa.JSON(), nullable=False),
        sa.Column("input_values", sa.JSON(), nullable=False),
        sa.Column("explanation", sa.JSON(), nullable=False),
        sa.Column("source_captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source_event_id", sa.String(256), nullable=False),
        sa.Column("calculation_version", sa.String(128), nullable=False),
        sa.Column("confidence", sa.Numeric(6, 4), nullable=False),
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("tenant_id", "asset_id", name="uq_risk_current"),
    )
    op.create_table(
        "risk_evaluation_history",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("risk_evaluation_id", sa.String(36), nullable=False),
        sa.Column("tenant_id", sa.String(128), nullable=False),
        sa.Column("asset_id", sa.String(128), nullable=False),
        sa.Column("risk_score", sa.Numeric(8, 4), nullable=False),
        sa.Column("risk_category", sa.String(64), nullable=False),
        sa.Column("factor_scores", sa.JSON(), nullable=False),
        sa.Column("input_values", sa.JSON(), nullable=False),
        sa.Column("explanation", sa.JSON(), nullable=False),
        sa.Column("source_captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source_event_id", sa.String(256), nullable=False),
        sa.Column("calculation_version", sa.String(128), nullable=False),
        sa.Column("confidence", sa.Numeric(6, 4), nullable=False),
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
    )
    for table in ("risk_evaluations", "risk_evaluation_history"):
        _common(table)
    op.create_index("ix_risk_history_asset_time", "risk_evaluation_history", ["tenant_id", "asset_id", "calculated_at"])

    op.create_table(
        "financial_evaluations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(128), nullable=False),
        sa.Column("asset_id", sa.String(128), nullable=False),
        sa.Column("assumption_version", sa.String(128), nullable=False),
        sa.Column("calculation_version", sa.String(128), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("scenarios", sa.JSON(), nullable=False),
        sa.Column("inputs_snapshot", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    _common("financial_evaluations")
    op.create_index("ix_financial_asset_time", "financial_evaluations", ["tenant_id", "asset_id", "created_at"])

    op.create_table(
        "source_registry",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(128), nullable=False),
        sa.Column("source_key", sa.String(256), nullable=False),
        sa.Column("source_type", sa.String(64), nullable=False),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("uri", sa.Text()),
        sa.Column("configuration", sa.JSON(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("tenant_id", "source_key", name="uq_source_key"),
    )
    _common("source_registry")
    op.create_table(
        "ingestion_records",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(128), nullable=False),
        sa.Column("source_id", sa.String(36), nullable=False),
        sa.Column("external_id", sa.String(256)),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("records_received", sa.Integer(), nullable=False),
        sa.Column("records_processed", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text()),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
    )
    _common("ingestion_records")
    op.create_index("ix_ingestion_source_time", "ingestion_records", ["tenant_id", "source_id", "started_at"])

    for table, exposure in (("vegetation_conditions", False), ("vegetation_exposures", True)):
        columns = [
            sa.Column("id", sa.String(36), primary_key=True),
            sa.Column("tenant_id", sa.String(128), nullable=False),
            sa.Column("asset_id", sa.String(128), nullable=False),
            sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("attributes", sa.JSON(), nullable=False),
            sa.Column("source_id", sa.String(36)),
        ]
        if exposure:
            columns.extend([sa.Column("exposure_score", sa.Numeric(8, 4), nullable=False), sa.Column("severity", sa.String(64)), sa.Column("geometry", sa.JSON())])
        else:
            columns.extend([sa.Column("condition_score", sa.Numeric(8, 4), nullable=False), sa.Column("fuel_type", sa.String(128)), sa.Column("height_m", sa.Numeric(8, 3)), sa.Column("distance_m", sa.Numeric(8, 3))])
        op.create_table(table, *columns)
        _common(table)
        op.create_index(f"ix_{table}_asset_time", table, ["tenant_id", "asset_id", "observed_at"])


def downgrade() -> None:
    for table in ("vegetation_exposures", "vegetation_conditions", "ingestion_records", "source_registry", "financial_evaluations", "risk_evaluation_history", "risk_evaluations"):
        op.drop_table(table)
