"""Create ai_interactions table

Revision ID: 006
Revises: 005
Create Date: 2025-01-27 05:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ai_interactions table
    op.create_table(
        'ai_interactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('interaction_type', sa.String(20), nullable=False),
        sa.Column('query_text', sa.Text(), nullable=False),
        sa.Column('query_audio_url', sa.String(500), nullable=True),
        sa.Column('intent', sa.String(100), nullable=True),
        sa.Column('response_text', sa.Text(), nullable=False),
        sa.Column('response_audio_url', sa.String(500), nullable=True),
        sa.Column('processing_duration_ms', sa.Integer(), nullable=True),
        sa.Column('confidence_score', sa.Numeric(5, 2), nullable=True),
        sa.Column('entities_json', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_ai_interactions_tenant_id', 'ai_interactions', ['tenant_id'])
    op.create_index('idx_ai_interactions_user_id', 'ai_interactions', ['user_id'])
    op.create_index('idx_ai_interactions_intent', 'ai_interactions', ['intent'])
    op.create_index('idx_ai_interactions_created_at', 'ai_interactions', ['created_at'])
    
    # Create check constraints
    op.create_check_constraint(
        'ck_interaction_type',
        'ai_interactions',
        "interaction_type IN ('voice', 'text')"
    )
    op.create_check_constraint(
        'ck_processing_duration_non_negative',
        'ai_interactions',
        'processing_duration_ms >= 0'
    )
    
    # Enable Row-Level Security
    op.execute('ALTER TABLE ai_interactions ENABLE ROW LEVEL SECURITY')
    
    # Create RLS policy
    op.execute("""
        CREATE POLICY ai_interactions_tenant_isolation ON ai_interactions
        FOR ALL
        USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid)
    """)


def downgrade() -> None:
    # Drop RLS policy
    op.execute('DROP POLICY IF EXISTS ai_interactions_tenant_isolation ON ai_interactions')
    
    # Disable RLS
    op.execute('ALTER TABLE ai_interactions DISABLE ROW LEVEL SECURITY')
    
    # Drop check constraints
    op.drop_constraint('ck_processing_duration_non_negative', 'ai_interactions', type_='check')
    op.drop_constraint('ck_interaction_type', 'ai_interactions', type_='check')
    
    # Drop indexes
    op.drop_index('idx_ai_interactions_created_at', table_name='ai_interactions')
    op.drop_index('idx_ai_interactions_intent', table_name='ai_interactions')
    op.drop_index('idx_ai_interactions_user_id', table_name='ai_interactions')
    op.drop_index('idx_ai_interactions_tenant_id', table_name='ai_interactions')
    
    # Drop table
    op.drop_table('ai_interactions')
