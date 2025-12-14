"""Initial base schema with audit logs and RLS setup

Revision ID: 001
Revises: 
Create Date: 2025-01-27 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable UUID extension
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    # Enable Row-Level Security (database-level setting)
    # Note: This is typically set at database creation, but we ensure it's enabled
    op.execute('ALTER DATABASE current_database() SET row_security = on')
    
    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()'))),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('entity_type', sa.String(50), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('changes_json', postgresql.JSONB, nullable=True),
        sa.Column('ip_address', postgresql.INET, nullable=True),
        sa.Column('user_agent', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for audit_logs
    op.create_index('idx_audit_logs_tenant_id', 'audit_logs', ['tenant_id'])
    op.create_index('idx_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('idx_audit_logs_entity', 'audit_logs', ['entity_type', 'entity_id'])
    op.create_index('idx_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('idx_audit_logs_created_at', 'audit_logs', ['created_at'])
    
    # Enable Row-Level Security on audit_logs table
    op.execute('ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY')
    
    # Create RLS policy for tenant isolation on audit_logs
    # Policy: Users can only see audit logs for their tenant
    op.execute("""
        CREATE POLICY audit_logs_tenant_isolation ON audit_logs
        FOR ALL
        USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid)
    """)


def downgrade() -> None:
    # Drop RLS policy
    op.execute('DROP POLICY IF EXISTS audit_logs_tenant_isolation ON audit_logs')
    
    # Disable RLS on audit_logs
    op.execute('ALTER TABLE audit_logs DISABLE ROW LEVEL SECURITY')
    
    # Drop indexes
    op.drop_index('idx_audit_logs_created_at', table_name='audit_logs')
    op.drop_index('idx_audit_logs_action', table_name='audit_logs')
    op.drop_index('idx_audit_logs_entity', table_name='audit_logs')
    op.drop_index('idx_audit_logs_user_id', table_name='audit_logs')
    op.drop_index('idx_audit_logs_tenant_id', table_name='audit_logs')
    
    # Drop audit_logs table
    op.drop_table('audit_logs')
