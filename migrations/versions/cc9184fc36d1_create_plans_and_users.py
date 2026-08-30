"""create_plans_and_users

Revision ID: cc9184fc36d1
Revises:
Create Date: 2026-08-02 16:13:56.832214

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "cc9184fc36d1"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # `plans` primero: `users` la referencia.
    op.create_table(
        "plans",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("max_drafts", sa.Integer(), nullable=False),
        sa.Column("max_sessions_per_day", sa.Integer(), nullable=False),
        sa.Column("history_retention_days", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_plans")),
        sa.UniqueConstraint("name", name=op.f("uq_plans_name")),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("surname_1", sa.String(length=100), nullable=False),
        sa.Column("surname_2", sa.String(length=100), nullable=True),
        sa.Column("nif", sa.String(length=16), nullable=False),
        sa.Column("birthdate", sa.Date(), nullable=False),
        sa.Column("marital_status", sa.String(length=32), nullable=True),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("email_verified", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("fiscal_address", sa.Text(), nullable=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("plan_id", sa.Uuid(), nullable=False),
        sa.Column("avatar_key", sa.String(length=512), nullable=True),
        sa.Column("status", sa.String(length=32), server_default=sa.text("'active'"), nullable=False),
        sa.Column("anonymized_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "preferences",
            postgresql.JSONB(none_as_null=True, astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["plan_id"], ["plans.id"], name=op.f("fk_users_plan_id_plans"), ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
        sa.UniqueConstraint("nif", name=op.f("uq_users_nif")),
    )
    op.create_index(op.f("ix_users_plan_id"), "users", ["plan_id"], unique=False)


def downgrade() -> None:
    # DESTRUCTIVE: elimina ambas tablas con todo su contenido.
    # `users` antes que `plans`: Postgres no deja borrar una tabla referenciada.
    op.drop_index(op.f("ix_users_plan_id"), table_name="users")
    op.drop_table("users")
    op.drop_table("plans")
