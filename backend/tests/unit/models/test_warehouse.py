"""
Unit tests for Warehouse model.
"""
import pytest
from uuid import uuid4
from sqlalchemy.exc import IntegrityError

from src.models.warehouse import Warehouse


def test_warehouse_creation(db_session, tenant_id):
    """Test creating a warehouse."""
    warehouse = Warehouse(
        tenant_id=tenant_id,
        name="Test Warehouse",
        address="123 Test St",
        city="Test City",
        country="Test Country",
        is_active=True
    )
    db_session.add(warehouse)
    db_session.commit()
    
    assert warehouse.id is not None
    assert warehouse.name == "Test Warehouse"
    assert warehouse.tenant_id == tenant_id
    assert warehouse.is_active is True


def test_warehouse_name_uniqueness_per_tenant(db_session, tenant_id):
    """Test that warehouse name must be unique per tenant."""
    warehouse1 = Warehouse(
        tenant_id=tenant_id,
        name="Test Warehouse",
        is_active=True
    )
    db_session.add(warehouse1)
    db_session.commit()
    
    # Same name, same tenant should fail
    warehouse2 = Warehouse(
        tenant_id=tenant_id,
        name="Test Warehouse",
        is_active=True
    )
    db_session.add(warehouse2)
    
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_warehouse_default_active(db_session, tenant_id):
    """Test that warehouse defaults to active."""
    warehouse = Warehouse(
        tenant_id=tenant_id,
        name="Test Warehouse"
    )
    db_session.add(warehouse)
    db_session.commit()
    
    assert warehouse.is_active is True


def test_warehouse_repr(db_session, tenant_id):
    """Test warehouse string representation."""
    warehouse = Warehouse(
        tenant_id=tenant_id,
        name="Test Warehouse",
        is_active=True
    )
    db_session.add(warehouse)
    db_session.commit()
    
    repr_str = repr(warehouse)
    assert "Warehouse" in repr_str
    assert "Test Warehouse" in repr_str
