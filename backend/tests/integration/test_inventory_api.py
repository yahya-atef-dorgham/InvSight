"""
Integration tests for inventory API endpoints.
"""
import pytest
from uuid import uuid4

from src.services.product_service import ProductService
from src.services.warehouse_service import WarehouseService
from src.services.inventory_service import InventoryService


def test_inventory_list_api(client, db_session, tenant_id, auth_token, test_product, test_warehouse, test_inventory):
    """Test GET /v1/inventory endpoint."""
    # Override tenant dependency
    from src.api.middleware.tenant import get_tenant_id
    from src.main import app
    
    def override_get_tenant_id():
        return tenant_id
    
    app.dependency_overrides[get_tenant_id] = override_get_tenant_id
    
    response = client.get(
        "/v1/inventory",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    app.dependency_overrides.clear()
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    
    # Check structure of inventory item
    item = data[0]
    assert "id" in item
    assert "product_sku" in item
    assert "product_name" in item
    assert "warehouse_name" in item
    assert "quantity" in item
    assert "is_low_stock" in item


def test_inventory_warehouse_filter(client, db_session, tenant_id, auth_token, test_product, test_warehouse, test_inventory):
    """Test inventory filtering by warehouse."""
    from src.api.middleware.tenant import get_tenant_id
    from src.main import app
    
    # Create another warehouse
    warehouse2 = WarehouseService.create(
        db_session,
        {
            "name": "Warehouse 2",
            "is_active": True
        },
        tenant_id
    )
    
    # Create inventory for second warehouse
    inventory2 = InventoryService.create_or_update(
        db_session,
        test_product.id,
        warehouse2.id,
        50.0,
        tenant_id
    )
    
    def override_get_tenant_id():
        return tenant_id
    
    app.dependency_overrides[get_tenant_id] = override_get_tenant_id
    
    # Get inventory for specific warehouse
    response = client.get(
        f"/v1/inventory?warehouse_id={warehouse2.id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    app.dependency_overrides.clear()
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["warehouse_id"] == str(warehouse2.id)
    assert data[0]["warehouse_name"] == "Warehouse 2"


def test_inventory_low_stock_filter(client, db_session, tenant_id, auth_token, test_product, test_warehouse):
    """Test inventory filtering by low stock."""
    from src.api.middleware.tenant import get_tenant_id
    from src.main import app
    
    # Create low stock inventory
    low_stock = InventoryService.create_or_update(
        db_session,
        test_product.id,
        test_warehouse.id,
        30.0,  # Below minimum
        tenant_id,
        minimum_stock=50.0
    )
    
    # Create normal stock inventory
    normal_stock = InventoryService.create_or_update(
        db_session,
        test_product.id,
        test_warehouse.id,
        100.0,  # Above minimum
        tenant_id,
        minimum_stock=50.0
    )
    
    def override_get_tenant_id():
        return tenant_id
    
    app.dependency_overrides[get_tenant_id] = override_get_tenant_id
    
    # Get only low stock items
    response = client.get(
        "/v1/inventory?low_stock=true",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    app.dependency_overrides.clear()
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(item["is_low_stock"] is True for item in data)


def test_inventory_tenant_isolation(client, db_session, auth_token, test_product, test_warehouse, test_inventory):
    """Test that inventory is properly isolated by tenant."""
    from src.api.middleware.tenant import get_tenant_id
    from src.main import app
    
    # Create another tenant
    tenant2 = uuid4()
    
    product2 = ProductService.create(
        db_session,
        {
            "sku": "T2-SKU-001",
            "name": "Tenant 2 Product",
            "unit_of_measure": "pieces"
        },
        tenant2
    )
    
    warehouse2 = WarehouseService.create(
        db_session,
        {
            "name": "Tenant 2 Warehouse",
            "is_active": True
        },
        tenant2
    )
    
    inventory2 = InventoryService.create_or_update(
        db_session,
        product2.id,
        warehouse2.id,
        200.0,
        tenant2
    )
    
    def override_get_tenant_id():
        return tenant2
    
    app.dependency_overrides[get_tenant_id] = override_get_tenant_id
    
    # Get inventory for tenant 2
    response = client.get(
        "/v1/inventory",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    app.dependency_overrides.clear()
    
    assert response.status_code == 200
    data = response.json()
    # Should only see tenant 2's inventory
    assert len(data) == 1
    assert data[0]["product_sku"] == "T2-SKU-001"
    assert data[0]["warehouse_name"] == "Tenant 2 Warehouse"
