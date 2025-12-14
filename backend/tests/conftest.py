"""
Pytest configuration and fixtures.
"""
import pytest
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from src.database.session import Base, get_db
from src.main import app
from src.models.product import Product
from src.models.warehouse import Warehouse
from src.models.inventory import Inventory


# Test database URL (use in-memory SQLite for testing)
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """Create a test client with database override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def tenant_id():
    """Generate a test tenant ID."""
    return uuid4()


@pytest.fixture
def test_product(db_session, tenant_id):
    """Create a test product."""
    product = Product(
        tenant_id=tenant_id,
        sku="TEST-SKU-001",
        name="Test Product",
        description="A test product",
        category="Electronics",
        unit_of_measure="pieces"
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


@pytest.fixture
def test_warehouse(db_session, tenant_id):
    """Create a test warehouse."""
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
    db_session.refresh(warehouse)
    return warehouse


@pytest.fixture
def test_inventory(db_session, tenant_id, test_product, test_warehouse):
    """Create test inventory."""
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
    db_session.refresh(inventory)
    return inventory


@pytest.fixture
def auth_token(tenant_id):
    """Generate a test JWT token."""
    from src.api.middleware.auth import create_access_token
    from datetime import timedelta
    
    token_data = {
        "sub": str(uuid4()),
        "tenant_id": str(tenant_id),
        "roles": ["inventory_manager"]
    }
    return create_access_token(token_data, expires_delta=timedelta(minutes=30))
