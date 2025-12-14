"""Create products, warehouses, and inventory tables

Revision ID: 002
Revises: 001
Create Date: 2025-01-27 01:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create products table
    op.create_table(
        'products',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sku', sa.String(100), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('unit_of_measure', sa.String(50), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create warehouses table
    op.create_table(
        'warehouses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('state', sa.String(100), nullable=True),
        sa.Column('country', sa.String(100), nullable=True),
        sa.Column('postal_code', sa.String(20), nullable=True),
        sa.Column('capacity_total', sa.Numeric(15, 2), nullable=True),
        sa.Column('capacity_unit', sa.String(50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create inventory table
    op.create_table(
        'inventory',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('warehouse_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quantity', sa.Numeric(15, 3), nullable=False, server_default='0'),
        sa.Column('reserved_quantity', sa.Numeric(15, 3), nullable=False, server_default='0'),
        sa.Column('minimum_stock', sa.Numeric(15, 3), nullable=True),
        sa.Column('safety_stock', sa.Numeric(15, 3), nullable=True),
        sa.Column('reorder_point', sa.Numeric(15, 3), nullable=True),
        sa.Column('last_movement_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], name='fk_inventory_product'),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], name='fk_inventory_warehouse'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for products
    op.create_index('idx_products_tenant_id', 'products', ['tenant_id'])
    op.create_index('idx_products_tenant_sku', 'products', ['tenant_id', 'sku'], unique=True)
    op.create_index('idx_products_category', 'products', ['category'])
    op.create_index('idx_products_sku', 'products', ['sku'])
    
    # Create unique constraint for products
    op.create_unique_constraint('uq_products_tenant_sku', 'products', ['tenant_id', 'sku'])
    
    # Create indexes for warehouses
    op.create_index('idx_warehouses_tenant_id', 'warehouses', ['tenant_id'])
    op.create_index('idx_warehouses_tenant_name', 'warehouses', ['tenant_id', 'name'], unique=True)
    op.create_index('idx_warehouses_active', 'warehouses', ['is_active'])
    
    # Create unique constraint for warehouses
    op.create_unique_constraint('uq_warehouses_tenant_name', 'warehouses', ['tenant_id', 'name'])
    
    # Create indexes for inventory
    op.create_index('idx_inventory_tenant_id', 'inventory', ['tenant_id'])
    op.create_index('idx_inventory_product_id', 'inventory', ['product_id'])
    op.create_index('idx_inventory_warehouse_id', 'inventory', ['warehouse_id'])
    op.create_index('idx_inventory_product_warehouse', 'inventory', ['tenant_id', 'product_id', 'warehouse_id'], unique=True)
    op.create_index('idx_inventory_low_stock', 'inventory', ['tenant_id', 'quantity', 'minimum_stock'])
    
    # Create unique constraint for inventory
    op.create_unique_constraint('uq_inventory_product_warehouse', 'inventory', ['tenant_id', 'product_id', 'warehouse_id'])
    
    # Create check constraints for inventory
    op.create_check_constraint('ck_inventory_quantity_non_negative', 'inventory', 'quantity >= 0')
    op.create_check_constraint('ck_inventory_reserved_non_negative', 'inventory', 'reserved_quantity >= 0')
    op.create_check_constraint('ck_inventory_reserved_leq_quantity', 'inventory', 'reserved_quantity <= quantity')
    
    # Enable Row-Level Security on new tables
    op.execute('ALTER TABLE products ENABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE warehouses ENABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE inventory ENABLE ROW LEVEL SECURITY')
    
    # Create RLS policies for tenant isolation
    op.execute("""
        CREATE POLICY products_tenant_isolation ON products
        FOR ALL
        USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid)
    """)
    
    op.execute("""
        CREATE POLICY warehouses_tenant_isolation ON warehouses
        FOR ALL
        USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid)
    """)
    
    op.execute("""
        CREATE POLICY inventory_tenant_isolation ON inventory
        FOR ALL
        USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid)
    """)


def downgrade() -> None:
    # Drop RLS policies
    op.execute('DROP POLICY IF EXISTS inventory_tenant_isolation ON inventory')
    op.execute('DROP POLICY IF EXISTS warehouses_tenant_isolation ON warehouses')
    op.execute('DROP POLICY IF EXISTS products_tenant_isolation ON products')
    
    # Disable RLS
    op.execute('ALTER TABLE inventory DISABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE warehouses DISABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE products DISABLE ROW LEVEL SECURITY')
    
    # Drop check constraints
    op.drop_constraint('ck_inventory_reserved_leq_quantity', 'inventory', type_='check')
    op.drop_constraint('ck_inventory_reserved_non_negative', 'inventory', type_='check')
    op.drop_constraint('ck_inventory_quantity_non_negative', 'inventory', type_='check')
    
    # Drop unique constraints
    op.drop_constraint('uq_inventory_product_warehouse', 'inventory', type_='unique')
    op.drop_constraint('uq_warehouses_tenant_name', 'warehouses', type_='unique')
    op.drop_constraint('uq_products_tenant_sku', 'products', type_='unique')
    
    # Drop indexes
    op.drop_index('idx_inventory_low_stock', table_name='inventory')
    op.drop_index('idx_inventory_product_warehouse', table_name='inventory')
    op.drop_index('idx_inventory_warehouse_id', table_name='inventory')
    op.drop_index('idx_inventory_product_id', table_name='inventory')
    op.drop_index('idx_inventory_tenant_id', table_name='inventory')
    op.drop_index('idx_warehouses_active', table_name='warehouses')
    op.drop_index('idx_warehouses_tenant_name', table_name='warehouses')
    op.drop_index('idx_warehouses_tenant_id', table_name='warehouses')
    op.drop_index('idx_products_sku', table_name='products')
    op.drop_index('idx_products_category', table_name='products')
    op.drop_index('idx_products_tenant_sku', table_name='products')
    op.drop_index('idx_products_tenant_id', table_name='products')
    
    # Drop tables (order matters due to foreign keys)
    op.drop_table('inventory')
    op.drop_table('warehouses')
    op.drop_table('products')
