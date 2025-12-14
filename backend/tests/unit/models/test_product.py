"""
Unit tests for Product model.
"""
import pytest
from uuid import uuid4
from sqlalchemy.exc import IntegrityError

from src.models.product import Product


def test_product_creation(db_session, tenant_id):
    """Test creating a product."""
    product = Product(
        tenant_id=tenant_id,
        sku="TEST-001",
        name="Test Product",
        description="A test product",
        category="Electronics",
        unit_of_measure="pieces"
    )
    db_session.add(product)
    db_session.commit()
    
    assert product.id is not None
    assert product.sku == "TEST-001"
    assert product.name == "Test Product"
    assert product.tenant_id == tenant_id


def test_product_sku_uniqueness_per_tenant(db_session, tenant_id):
    """Test that SKU must be unique per tenant."""
    product1 = Product(
        tenant_id=tenant_id,
        sku="TEST-001",
        name="Product 1",
        unit_of_measure="pieces"
    )
    db_session.add(product1)
    db_session.commit()
    
    # Same SKU, same tenant should fail
    product2 = Product(
        tenant_id=tenant_id,
        sku="TEST-001",
        name="Product 2",
        unit_of_measure="pieces"
    )
    db_session.add(product2)
    
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_product_sku_different_tenants(db_session):
    """Test that same SKU can exist for different tenants."""
    tenant1 = uuid4()
    tenant2 = uuid4()
    
    product1 = Product(
        tenant_id=tenant1,
        sku="TEST-001",
        name="Product 1",
        unit_of_measure="pieces"
    )
    product2 = Product(
        tenant_id=tenant2,
        sku="TEST-001",
        name="Product 2",
        unit_of_measure="pieces"
    )
    
    db_session.add(product1)
    db_session.add(product2)
    db_session.commit()
    
    assert product1.id != product2.id
    assert product1.sku == product2.sku
    assert product1.tenant_id != product2.tenant_id


def test_product_repr(db_session, tenant_id):
    """Test product string representation."""
    product = Product(
        tenant_id=tenant_id,
        sku="TEST-001",
        name="Test Product",
        unit_of_measure="pieces"
    )
    db_session.add(product)
    db_session.commit()
    
    repr_str = repr(product)
    assert "Product" in repr_str
    assert "TEST-001" in repr_str
    assert "Test Product" in repr_str
