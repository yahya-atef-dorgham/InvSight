"""Create suppliers, purchase_orders, and purchase_order_items tables

Revision ID: 005
Revises: 004
Create Date: 2025-01-27 04:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create suppliers table
    op.create_table(
        'suppliers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('contact_email', sa.String(255), nullable=True),
        sa.Column('contact_phone', sa.String(50), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('state', sa.String(100), nullable=True),
        sa.Column('country', sa.String(100), nullable=True),
        sa.Column('postal_code', sa.String(20), nullable=True),
        sa.Column('payment_terms', sa.String(100), nullable=True),
        sa.Column('tax_id', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('performance_score', sa.Numeric(5, 2), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create purchase_orders table
    op.create_table(
        'purchase_orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_number', sa.String(100), nullable=False),
        sa.Column('supplier_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='draft'),
        sa.Column('total_amount', sa.Numeric(15, 2), nullable=True),
        sa.Column('currency', sa.String(3), nullable=False, server_default='USD'),
        sa.Column('expected_delivery_date', sa.Date(), nullable=True),
        sa.Column('actual_delivery_date', sa.Date(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('received_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancelled_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('cancellation_reason', sa.Text(), nullable=True),
        sa.Column('ai_recommendation_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['supplier_id'], ['suppliers.id'], name='fk_po_supplier'),
        sa.ForeignKeyConstraint(['ai_recommendation_id'], ['ai_recommendations.id'], name='fk_po_ai_recommendation'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create purchase_order_items table
    op.create_table(
        'purchase_order_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('uuid_generate_v4()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('purchase_order_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('warehouse_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('quantity', sa.Numeric(15, 3), nullable=False),
        sa.Column('unit_cost', sa.Numeric(15, 2), nullable=False),
        sa.Column('total_cost', sa.Numeric(15, 2), nullable=False),
        sa.Column('received_quantity', sa.Numeric(15, 3), nullable=False, server_default='0'),
        sa.Column('line_number', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['purchase_order_id'], ['purchase_orders.id'], name='fk_po_item_po'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], name='fk_po_item_product'),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], name='fk_po_item_warehouse'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for suppliers
    op.create_index('idx_suppliers_tenant_id', 'suppliers', ['tenant_id'])
    op.create_index('idx_suppliers_tenant_name', 'suppliers', ['tenant_id', 'name'], unique=True)
    op.create_index('idx_suppliers_active', 'suppliers', ['is_active'])
    
    # Create unique constraint for suppliers
    op.create_unique_constraint('uq_suppliers_tenant_name', 'suppliers', ['tenant_id', 'name'])
    
    # Create indexes for purchase_orders
    op.create_index('idx_purchase_orders_tenant_id', 'purchase_orders', ['tenant_id'])
    op.create_index('idx_purchase_orders_tenant_order_number', 'purchase_orders', ['tenant_id', 'order_number'], unique=True)
    op.create_index('idx_purchase_orders_supplier_id', 'purchase_orders', ['supplier_id'])
    op.create_index('idx_purchase_orders_status', 'purchase_orders', ['status'])
    op.create_index('idx_purchase_orders_created_at', 'purchase_orders', ['created_at'])
    op.create_index('idx_purchase_orders_ai_recommendation_id', 'purchase_orders', ['ai_recommendation_id'])
    
    # Create unique constraint for purchase_orders
    op.create_unique_constraint('uq_purchase_orders_tenant_order_number', 'purchase_orders', ['tenant_id', 'order_number'])
    
    # Create indexes for purchase_order_items
    op.create_index('idx_purchase_order_items_tenant_id', 'purchase_order_items', ['tenant_id'])
    op.create_index('idx_purchase_order_items_purchase_order_id', 'purchase_order_items', ['purchase_order_id'])
    op.create_index('idx_purchase_order_items_product_id', 'purchase_order_items', ['product_id'])
    
    # Create check constraints for purchase_orders
    op.create_check_constraint(
        'ck_po_status',
        'purchase_orders',
        "status IN ('draft', 'approved', 'sent', 'partially_received', 'received', 'cancelled')"
    )
    
    # Create check constraints for purchase_order_items
    op.create_check_constraint('ck_po_item_quantity_positive', 'purchase_order_items', 'quantity > 0')
    op.create_check_constraint('ck_po_item_cost_non_negative', 'purchase_order_items', 'unit_cost >= 0')
    op.create_check_constraint('ck_po_item_received_non_negative', 'purchase_order_items', 'received_quantity >= 0')
    op.create_check_constraint('ck_po_item_received_leq_quantity', 'purchase_order_items', 'received_quantity <= quantity')
    
    # Enable Row-Level Security
    op.execute('ALTER TABLE suppliers ENABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE purchase_orders ENABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE purchase_order_items ENABLE ROW LEVEL SECURITY')
    
    # Create RLS policies
    op.execute("""
        CREATE POLICY suppliers_tenant_isolation ON suppliers
        FOR ALL
        USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid)
    """)
    
    op.execute("""
        CREATE POLICY purchase_orders_tenant_isolation ON purchase_orders
        FOR ALL
        USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid)
    """)
    
    op.execute("""
        CREATE POLICY purchase_order_items_tenant_isolation ON purchase_order_items
        FOR ALL
        USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid)
    """)


def downgrade() -> None:
    # Drop RLS policies
    op.execute('DROP POLICY IF EXISTS purchase_order_items_tenant_isolation ON purchase_order_items')
    op.execute('DROP POLICY IF EXISTS purchase_orders_tenant_isolation ON purchase_orders')
    op.execute('DROP POLICY IF EXISTS suppliers_tenant_isolation ON suppliers')
    
    # Disable RLS
    op.execute('ALTER TABLE purchase_order_items DISABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE purchase_orders DISABLE ROW LEVEL SECURITY')
    op.execute('ALTER TABLE suppliers DISABLE ROW LEVEL SECURITY')
    
    # Drop check constraints
    op.drop_constraint('ck_po_item_received_leq_quantity', 'purchase_order_items', type_='check')
    op.drop_constraint('ck_po_item_received_non_negative', 'purchase_order_items', type_='check')
    op.drop_constraint('ck_po_item_cost_non_negative', 'purchase_order_items', type_='check')
    op.drop_constraint('ck_po_item_quantity_positive', 'purchase_order_items', type_='check')
    op.drop_constraint('ck_po_status', 'purchase_orders', type_='check')
    
    # Drop indexes
    op.drop_index('idx_purchase_order_items_product_id', table_name='purchase_order_items')
    op.drop_index('idx_purchase_order_items_purchase_order_id', table_name='purchase_order_items')
    op.drop_index('idx_purchase_order_items_tenant_id', table_name='purchase_order_items')
    op.drop_index('idx_purchase_orders_ai_recommendation_id', table_name='purchase_orders')
    op.drop_index('idx_purchase_orders_created_at', table_name='purchase_orders')
    op.drop_index('idx_purchase_orders_status', table_name='purchase_orders')
    op.drop_index('idx_purchase_orders_supplier_id', table_name='purchase_orders')
    op.drop_index('idx_purchase_orders_tenant_order_number', table_name='purchase_orders')
    op.drop_index('idx_purchase_orders_tenant_id', table_name='purchase_orders')
    op.drop_index('idx_suppliers_active', table_name='suppliers')
    op.drop_index('idx_suppliers_tenant_name', table_name='suppliers')
    op.drop_index('idx_suppliers_tenant_id', table_name='suppliers')
    
    # Drop unique constraints
    op.drop_constraint('uq_purchase_orders_tenant_order_number', 'purchase_orders', type_='unique')
    op.drop_constraint('uq_suppliers_tenant_name', 'suppliers', type_='unique')
    
    # Drop tables (order matters due to foreign keys)
    op.drop_table('purchase_order_items')
    op.drop_table('purchase_orders')
    op.drop_table('suppliers')
