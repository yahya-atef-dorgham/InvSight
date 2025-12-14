"""Create forecasts and ai_recommendations tables

Revision ID: 004
Revises: 003
Create Date: 2025-01-27 03:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create forecasts table
    op.create_table(
        'forecasts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('warehouse_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('forecast_horizon_days', sa.Integer(), nullable=False),
        sa.Column('forecast_date', sa.Date(), nullable=False),
        sa.Column('predicted_demand', sa.Numeric(15, 3), nullable=False),
        sa.Column('confidence_lower', sa.Numeric(15, 3), nullable=True),
        sa.Column('confidence_upper', sa.Numeric(15, 3), nullable=True),
        sa.Column('confidence_level', sa.Numeric(5, 2), nullable=True),
        sa.Column('model_version', sa.String(50), nullable=False),
        sa.Column('model_type', sa.String(50), nullable=True),
        sa.Column('generated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('features_json', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], name='fk_forecast_product'),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], name='fk_forecast_warehouse'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create ai_recommendations table
    op.create_table(
        'ai_recommendations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('recommendation_type', sa.String(50), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('warehouse_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('forecast_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('recommended_value', sa.Numeric(15, 3), nullable=True),
        sa.Column('current_value', sa.Numeric(15, 3), nullable=True),
        sa.Column('urgency_score', sa.Numeric(5, 2), nullable=True),
        sa.Column('confidence_score', sa.Numeric(5, 2), nullable=True),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('explanation_json', postgresql.JSONB, nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('actioned_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('actioned_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('purchase_order_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], name='fk_recommendation_product'),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], name='fk_recommendation_warehouse'),
        sa.ForeignKeyConstraint(['forecast_id'], ['forecasts.id'], name='fk_recommendation_forecast'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for forecasts
    op.create_index('idx_forecasts_tenant_id', 'forecasts', ['tenant_id'])
    op.create_index('idx_forecasts_product_id', 'forecasts', ['product_id'])
    op.create_index('idx_forecasts_warehouse_id', 'forecasts', ['warehouse_id'])
    op.create_index('idx_forecasts_product_warehouse', 'forecasts', ['product_id', 'warehouse_id'])
    op.create_index('idx_forecasts_horizon_date', 'forecasts', ['forecast_horizon_days', 'forecast_date'])
    op.create_index('idx_forecasts_model_version', 'forecasts', ['model_version'])
    op.create_index('idx_forecasts_generated_at', 'forecasts', ['generated_at'])
    op.create_index('idx_forecasts_forecast_date', 'forecasts', ['forecast_date'])
    
    # Create unique constraint for forecasts
    op.create_unique_constraint(
        'uq_forecasts_unique',
        'forecasts',
        ['tenant_id', 'product_id', 'warehouse_id', 'forecast_horizon_days', 'forecast_date']
    )
    
    # Create indexes for ai_recommendations
    op.create_index('idx_ai_recommendations_tenant_id', 'ai_recommendations', ['tenant_id'])
    op.create_index('idx_ai_recommendations_product_id', 'ai_recommendations', ['product_id'])
    op.create_index('idx_ai_recommendations_warehouse_id', 'ai_recommendations', ['warehouse_id'])
    op.create_index('idx_ai_recommendations_product_warehouse', 'ai_recommendations', ['product_id', 'warehouse_id'])
    op.create_index('idx_ai_recommendations_type_status', 'ai_recommendations', ['recommendation_type', 'status'])
    op.create_index('idx_ai_recommendations_urgency', 'ai_recommendations', ['urgency_score'])
    op.create_index('idx_ai_recommendations_created_at', 'ai_recommendations', ['created_at'])
    op.create_index('idx_ai_recommendations_status', 'ai_recommendations', ['status'])
    
    # Create check constraints for forecasts
    op.create_check_constraint('ck_forecast_horizon', 'forecasts', 'forecast_horizon_days IN (7, 30, 90)')
    op.create_check_constraint('ck_forecast_demand_non_negative', 'forecasts', 'predicted_demand >= 0')
    
    # Create check constraints for ai_recommendations
    op.create_check_constraint(
        'ck_recommendation_type',
        'ai_recommendations',
        "recommendation_type IN ('reorder_point', 'reorder_quantity', 'purchase_order')"
    )
    op.create_check_constraint(
        'ck_recommendation_status',
        'ai_recommendations',
        "status IN ('active', 'approved', 'rejected', 'superseded')"
    )
    op.create_check_constraint(
        'ck_recommendation_value_non_negative',
        'ai_recommendations',
        'recommended_value >= 0'
    )
    
    # Enable Row-Level Security
    op.execute('ALTER TABLE forecasts ENABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE ai_recommendations ENABLE ROW LEVEL SECURITY')
    
    # Create RLS policies
    op.execute("""
        CREATE POLICY forecasts_tenant_isolation ON forecasts
        FOR ALL
        USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid)
    """)
    
    op.execute("""
        CREATE POLICY ai_recommendations_tenant_isolation ON ai_recommendations
        FOR ALL
        USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid)
    """)


def downgrade() -> None:
    # Drop RLS policies
    op.execute('DROP POLICY IF EXISTS ai_recommendations_tenant_isolation ON ai_recommendations')
    op.execute('DROP POLICY IF EXISTS forecasts_tenant_isolation ON forecasts')
    
    # Disable RLS
    op.execute('ALTER TABLE ai_recommendations DISABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE forecasts DISABLE ROW LEVEL SECURITY')
    
    # Drop check constraints
    op.drop_constraint('ck_recommendation_value_non_negative', 'ai_recommendations', type_='check')
    op.drop_constraint('ck_recommendation_status', 'ai_recommendations', type_='check')
    op.drop_constraint('ck_recommendation_type', 'ai_recommendations', type_='check')
    op.drop_constraint('ck_forecast_demand_non_negative', 'forecasts', type_='check')
    op.drop_constraint('ck_forecast_horizon', 'forecasts', type_='check')
    
    # Drop indexes
    op.drop_index('idx_ai_recommendations_status', table_name='ai_recommendations')
    op.drop_index('idx_ai_recommendations_created_at', table_name='ai_recommendations')
    op.drop_index('idx_ai_recommendations_urgency', table_name='ai_recommendations')
    op.drop_index('idx_ai_recommendations_type_status', table_name='ai_recommendations')
    op.drop_index('idx_ai_recommendations_product_warehouse', table_name='ai_recommendations')
    op.drop_index('idx_ai_recommendations_warehouse_id', table_name='ai_recommendations')
    op.drop_index('idx_ai_recommendations_product_id', table_name='ai_recommendations')
    op.drop_index('idx_ai_recommendations_tenant_id', table_name='ai_recommendations')
    op.drop_index('idx_forecasts_forecast_date', table_name='forecasts')
    op.drop_index('idx_forecasts_generated_at', table_name='forecasts')
    op.drop_index('idx_forecasts_model_version', table_name='forecasts')
    op.drop_index('idx_forecasts_horizon_date', table_name='forecasts')
    op.drop_index('idx_forecasts_product_warehouse', table_name='forecasts')
    op.drop_index('idx_forecasts_warehouse_id', table_name='forecasts')
    op.drop_index('idx_forecasts_product_id', table_name='forecasts')
    op.drop_index('idx_forecasts_tenant_id', table_name='forecasts')
    
    # Drop unique constraints
    op.drop_constraint('uq_forecasts_unique', 'forecasts', type_='unique')
    
    # Drop tables
    op.drop_table('ai_recommendations')
    op.drop_table('forecasts')
