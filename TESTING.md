# Testing Guide for User Story 1

This guide explains how to run tests for the Inventory Dashboard feature.

## Prerequisites

1. **Backend Dependencies**: Install Python dependencies
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Frontend Dependencies**: Install Node.js dependencies
   ```bash
   cd frontend
   npm install
   ```

3. **Database**: For integration tests, you'll need a test database. Tests use SQLite by default.

## Running Backend Tests

### Unit Tests

Test individual models (Product, Warehouse, Inventory):

```bash
cd backend
pytest tests/unit/models/ -v
```

Run specific test file:
```bash
pytest tests/unit/models/test_product.py -v
pytest tests/unit/models/test_warehouse.py -v
pytest tests/unit/models/test_inventory.py -v
```

### Integration Tests

Test API endpoints:

```bash
cd backend
pytest tests/integration/ -v
```

Run specific integration test:
```bash
pytest tests/integration/test_inventory_api.py -v
```

### Run All Backend Tests

```bash
cd backend
pytest tests/ -v
```

## Running Frontend Tests

### Unit Tests (Jest + React Testing Library)

```bash
cd frontend
npm test
```

Run in watch mode:
```bash
npm test -- --watch
```

Run specific test:
```bash
npm test -- InventoryDashboard.test.tsx
```

### E2E Tests (Playwright)

First, install Playwright browsers:
```bash
cd frontend
npx playwright install
```

Run E2E tests:
```bash
npm run test:e2e
```

Run E2E tests with UI:
```bash
npm run test:e2e:ui
```

**Note**: E2E tests require both backend and frontend servers to be running.

## Manual Testing

### 1. Start Backend Server

```bash
cd backend
# Set environment variables
export DATABASE_URL="postgresql://user:pass@localhost:5432/inventory_db"
export SECRET_KEY="your-secret-key"

# Run migrations
alembic upgrade head

# Start server
uvicorn src.main:app --reload --port 8000
```

### 2. Start Frontend Server

```bash
cd frontend
npm start
```

### 3. Test the Dashboard

1. Navigate to `http://localhost:3000/login`
2. Login with credentials:
   - Tenant ID: Any UUID (e.g., `550e8400-e29b-41d4-a716-446655440000`)
   - Username: Any username
   - Password: Any password
3. You should be redirected to `/inventory` dashboard
4. Verify:
   - Dashboard title is visible
   - Statistics cards show totals
   - Inventory table displays (or empty state)
   - Warehouse filter works
   - Low stock toggle works
   - Real-time updates (if WebSocket connected)

### 4. Test API Endpoints

Using curl or Postman:

```bash
# Get auth token
curl -X POST http://localhost:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass",
    "tenant_id": "550e8400-e29b-41d4-a716-446655440000"
  }'

# Use token to get inventory
curl http://localhost:8000/v1/inventory \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Filter by warehouse
curl "http://localhost:8000/v1/inventory?warehouse_id=WAREHOUSE_ID" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Get low stock items
curl "http://localhost:8000/v1/inventory?low_stock=true" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Test Coverage

To check test coverage:

### Backend
```bash
cd backend
pytest --cov=src --cov-report=html tests/
```

### Frontend
```bash
cd frontend
npm test -- --coverage
```

## Troubleshooting

### Backend Tests Fail

- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that test database is accessible
- Verify pytest is installed: `pip install pytest pytest-asyncio httpx`

### Frontend Tests Fail

- Ensure dependencies are installed: `npm install`
- Check that `setupTests.ts` exists
- Verify testing libraries are installed

### E2E Tests Fail

- Ensure both backend and frontend servers are running
- Check that Playwright browsers are installed: `npx playwright install`
- Verify the base URL in `playwright.config.ts` matches your frontend URL

## Expected Test Results

### Backend Unit Tests
- ✅ Product model creation and validation
- ✅ Warehouse model creation and validation  
- ✅ Inventory model creation and calculations
- ✅ Tenant isolation constraints

### Backend Integration Tests
- ✅ Inventory list API returns correct data
- ✅ Warehouse filtering works
- ✅ Low stock filtering works
- ✅ Tenant isolation enforced

### Frontend Unit Tests
- ✅ Dashboard renders correctly
- ✅ Statistics cards display
- ✅ Components handle loading states

### Frontend E2E Tests
- ✅ User can navigate to dashboard
- ✅ Dashboard displays inventory data
- ✅ Filters work correctly
- ✅ Real-time updates function
