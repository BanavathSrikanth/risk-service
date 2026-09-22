"""Add durable transitional records and ROI risk linkage.

Revision ID: 0002_tenant_records_and_roi_link
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_tenant_records_and_roi_link"
down_revision = "0001_persistence_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "financial_evaluations",
        sa.Column("risk_evaluation_id", sa.String(36), nullable=True),
    )
    op.create_index(
        "ix_financial_risk_evaluation",
        "financial_evaluations",
        ["tenant_id", "risk_evaluation_id"],
    )
    op.create_table(
        "tenant_records",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(128), nullable=False),
        sa.Column("entity_type", sa.String(64), nullable=False),
        sa.Column("entity_id", sa.String(256), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint(
            "tenant_id", "entity_type", "entity_id", name="uq_tenant_record"
        ),
    )
    op.create_index(
        "ix_tenant_record_lookup",
        "tenant_records",
        ["tenant_id", "entity_type"],
    )


def downgrade() -> None:
    op.drop_index("ix_tenant_record_lookup", table_name="tenant_records")
    op.drop_table("tenant_records")
    op.drop_index(
        "ix_financial_risk_evaluation", table_name="financial_evaluations"
    )
    op.drop_column("financial_evaluations", "risk_evaluation_id")
