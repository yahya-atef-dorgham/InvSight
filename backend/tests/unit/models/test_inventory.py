"""
Unit tests for Inventory model.
"""
import pytest
from decimal import Decimal
from uuid import uuid4

from src.models.inventory import Inventory


def test_inventory_creation(db_session, tenant_id, test_product, test_warehouse):
    """Test creating inventory."""
    inventory = Inventory(
        tenant_id=tenant_id,
        product_id=test_product.id,
        warehouse_id=test_warehouse.id,
        quantity=100.0,
        minimum_stock=50.0,
        safety_stock=25.0
    )
    db_session.add(inventory)
    db_session.commit()
    
    assert inventory.id is not None
    assert inventory.quantity == Decimal('100.0')
    assert inventory.minimum_stock == Decimal('50.0')
    assert inventory.version == 0


def test_inventory_available_quantity(db_session, tenant_id, test_product, test_warehouse):
    """Test available quantity calculation."""
    inventory = Inventory(
        tenant_id=tenant_id,
        product_id=test_product.id,
        warehouse_id=test_warehouse.id,
        quantity=100.0,
        reserved_quantity=20.0
    )
    db_session.add(inventory)
    db_session.commit()
    
    assert inventory.available_quantity == 80.0


def test_inventory_low_stock_detection(db_session, tenant_id, test_product, test_warehouse):
    """Test low stock detection."""
    # Low stock
    inventory_low = Inventory(
        tenant_id=tenant_id,
        product_id=test_product.id,
        warehouse_id=test_warehouse.id,
        quantity=30.0,
        minimum_stock=50.0
    )
    assert inventory_low.is_low_stock is True
    
    # Not low stock
    inventory_ok = Inventory(
        tenant_id=tenant_id,
        product_id=test_product.id,
        warehouse_id=test_warehouse.id,
        quantity=100.0,
        minimum_stock=50.0
    )
    assert inventory_ok.is_low_stock is False
    
    # No minimum stock set
    inventory_no_min = Inventory(
        tenant_id=tenant_id,
        product_id=test_product.id,
        warehouse_id=test_warehouse.id,
        quantity=10.0,
        minimum_stock=None
    )
    assert inventory_no_min.is_low_stock is False


def test_inventory_unique_per_product_warehouse(db_session, tenant_id, test_product, test_warehouse):
    """Test that inventory is unique per product-warehouse combination."""
    inventory1 = Inventory(
        tenant_id=tenant_id,
        product_id=test_product.id,
        warehouse_id=test_warehouse.id,
        quantity=100.0
    )
    db_session.add(inventory1)
    db_session.commit()
    
    # Same product-warehouse should fail
    inventory2 = Inventory(
        tenant_id=tenant_id,
        product_id=test_product.id,
        warehouse_id=test_warehouse.id,
        quantity=200.0
    )
    db_session.add(inventory2)
    
    with pytest.raises(Exception):  # IntegrityError or similar
        db_session.commit()


def test_inventory_repr(db_session, tenant_id, test_product, test_warehouse):
    """Test inventory string representation."""
    inventory = Inventory(
        tenant_id=tenant_id,
        product_id=test_product.id,
        warehouse_id=test_warehouse.id,
        quantity=100.0
    )
    db_session.add(inventory)
    db_session.commit()
    
    repr_str = repr(inventory)
    assert "Inventory" in repr_str
    assert str(test_product.id) in repr_str or "product_id" in repr_str
