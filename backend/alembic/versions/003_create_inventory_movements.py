"""Create inventory_movements table

Revision ID: 003
Revises: 002
Create Date: 2025-01-27 02:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create inventory_movements table
    op.create_table(
        'inventory_movements',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('movement_type', sa.String(20), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('source_warehouse_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('destination_warehouse_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('quantity', sa.Numeric(15, 3), nullable=False),
        sa.Column('quantity_before', sa.Numeric(15, 3), nullable=True),
        sa.Column('quantity_after', sa.Numeric(15, 3), nullable=True),
        sa.Column('reference_number', sa.String(100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('performed_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('performed_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], name='fk_movement_product'),
        sa.ForeignKeyConstraint(['source_warehouse_id'], ['warehouses.id'], name='fk_movement_source_warehouse'),
        sa.ForeignKeyConstraint(['destination_warehouse_id'], ['warehouses.id'], name='fk_movement_destination_warehouse'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_inventory_movements_tenant_id', 'inventory_movements', ['tenant_id'])
    op.create_index('idx_inventory_movements_product_id', 'inventory_movements', ['product_id'])
    op.create_index('idx_inventory_movements_performed_at', 'inventory_movements', ['performed_at'])
    op.create_index('idx_inventory_movements_performed_by', 'inventory_movements', ['performed_by'])
    op.create_index('idx_inventory_movements_type', 'inventory_movements', ['movement_type'])
    op.create_index('idx_inventory_movements_source_warehouse', 'inventory_movements', ['source_warehouse_id'])
    op.create_index('idx_inventory_movements_destination_warehouse', 'inventory_movements', ['destination_warehouse_id'])
    
    # Create check constraints
    op.create_check_constraint(
        'ck_movement_type',
        'inventory_movements',
        "movement_type IN ('inbound', 'outbound', 'transfer')"
    )
    op.create_check_constraint(
        'ck_movement_warehouses',
        'inventory_movements',
        "(movement_type = 'inbound' AND source_warehouse_id IS NULL AND destination_warehouse_id IS NOT NULL) OR "
        "(movement_type = 'outbound' AND source_warehouse_id IS NOT NULL AND destination_warehouse_id IS NULL) OR "
        "(movement_type = 'transfer' AND source_warehouse_id IS NOT NULL AND destination_warehouse_id IS NOT NULL)"
    )
    op.create_check_constraint(
        'ck_movement_quantity_positive',
        'inventory_movements',
        'quantity > 0'
    )
    
    # Enable Row-Level Security
    op.execute('ALTER TABLE inventory_movements ENABLE ROW LEVEL SECURITY')
    
    # Create RLS policy
    op.execute("""
        CREATE POLICY inventory_movements_tenant_isolation ON inventory_movements
        FOR ALL
        USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid)
    """)


def downgrade() -> None:
    # Drop RLS policy
    op.execute('DROP POLICY IF EXISTS inventory_movements_tenant_isolation ON inventory_movements')
    
    # Disable RLS
    op.execute('ALTER TABLE inventory_movements DISABLE ROW LEVEL SECURITY')
    
    # Drop check constraints
    op.drop_constraint('ck_movement_quantity_positive', 'inventory_movements', type_='check')
    op.drop_constraint('ck_movement_warehouses', 'inventory_movements', type_='check')
    op.drop_constraint('ck_movement_type', 'inventory_movements', type_='check')
    
    # Drop indexes
    op.drop_index('idx_inventory_movements_destination_warehouse', table_name='inventory_movements')
    op.drop_index('idx_inventory_movements_source_warehouse', table_name='inventory_movements')
    op.drop_index('idx_inventory_movements_type', table_name='inventory_movements')
    op.drop_index('idx_inventory_movements_performed_by', table_name='inventory_movements')
    op.drop_index('idx_inventory_movements_performed_at', table_name='inventory_movements')
    op.drop_index('idx_inventory_movements_product_id', table_name='inventory_movements')
    op.drop_index('idx_inventory_movements_tenant_id', table_name='inventory_movements')
    
    # Drop table
    op.drop_table('inventory_movements')
