# Test Checklist - All User Stories

## Quick Test Verification

### Prerequisites Check
- [ ] Python 3.8+ installed and in PATH
- [ ] Node.js 16+ installed
- [ ] PostgreSQL running (for production) or SQLite (for tests)
- [ ] All dependencies installed:
  - Backend: `pip install -r requirements.txt`
  - Frontend: `npm install`
  - AI Service: `pip install -r requirements.txt`
  - Voice Service: `pip install -r requirements.txt`

### Database Setup
- [ ] Run migrations: `cd backend && alembic upgrade head`
- [ ] Verify tables created: `audit_logs`, `products`, `warehouses`, `inventory`, `inventory_movements`, `forecasts`, `ai_recommendations`, `suppliers`, `purchase_orders`, `purchase_order_items`, `ai_interactions`

### Backend Tests

#### Unit Tests
- [ ] `pytest tests/unit/models/test_product.py -v`
- [ ] `pytest tests/unit/models/test_warehouse.py -v`
- [ ] `pytest tests/unit/models/test_inventory.py -v`

#### Integration Tests
- [ ] `pytest tests/integration/test_inventory_api.py -v`

### Frontend Tests
- [ ] `npm test` (unit tests)
- [ ] `npm run test:e2e` (E2E tests - requires servers running)

### Manual Testing Checklist

#### User Story 1 - Inventory Dashboard
- [ ] Login at `/login`
- [ ] Navigate to `/inventory`
- [ ] Verify dashboard displays inventory items
- [ ] Test warehouse filter
- [ ] Test low stock toggle
- [ ] Verify real-time updates (if WebSocket connected)

#### User Story 2 - Inventory Movements
- [ ] Navigate to `/movements`
- [ ] Create inbound movement
- [ ] Verify inventory updates
- [ ] Create outbound movement
- [ ] Create transfer movement
- [ ] View movement history

#### User Story 3 - AI Recommendations
- [ ] Navigate to `/recommendations`
- [ ] Generate a recommendation
- [ ] View recommendation details
- [ ] Check explanation
- [ ] View forecast charts (if data available)

#### User Story 4 - Purchase Orders
- [ ] Navigate to `/purchase-orders`
- [ ] Create PO from recommendation
- [ ] Approve purchase order
- [ ] Receive PO items
- [ ] Verify inventory updated after receipt

#### User Story 5 - Voice Assistant
- [ ] Navigate to `/voice`
- [ ] Test voice input (if browser supports Web Speech API)
- [ ] Test text input fallback
- [ ] Verify response playback
- [ ] Check interaction history

### API Testing (using curl/Postman)

#### Authentication
```bash
# Login
curl -X POST http://localhost:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test", "tenant_id": "..."}'
```

#### Inventory
```bash
# Get inventory
curl http://localhost:8000/v1/inventory \
  -H "Authorization: Bearer TOKEN"

# Create movement
curl -X POST http://localhost:8000/v1/inventory/movement \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"movement_type": "inbound", "product_id": "...", ...}'
```

#### Recommendations
```bash
# Get recommendations
curl http://localhost:8000/v1/recommendations \
  -H "Authorization: Bearer TOKEN"
```

#### Purchase Orders
```bash
# Get purchase orders
curl http://localhost:8000/v1/purchase-orders \
  -H "Authorization: Bearer TOKEN"

# Approve PO
curl -X POST http://localhost:8000/v1/purchase-orders/{id}/approve \
  -H "Authorization: Bearer TOKEN"
```

#### Voice
```bash
# Process voice query
curl -X POST http://localhost:8000/v1/ai/voice/query \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query_text": "What is the stock level?", "interaction_type": "voice"}'
```

## Service Health Checks

- [ ] Backend: `curl http://localhost:8000/health`
- [ ] AI Service: `curl http://localhost:8001/health`
- [ ] Voice Service: `curl http://localhost:8002/health`
- [ ] Frontend: Open `http://localhost:3000` in browser

## Common Issues & Fixes

### Issue: Python not found
**Fix**: Use `py` instead of `python` on Windows, or add Python to PATH

### Issue: Import errors
**Fix**: Ensure you're in the correct directory and virtual environment is activated

### Issue: Database connection errors
**Fix**: Check DATABASE_URL in `.env` or settings.py

### Issue: CORS errors
**Fix**: Verify CORS origins in `backend/src/config/settings.py`

### Issue: Web Speech API not working
**Fix**: Use Chrome/Edge (best support) or use text input fallback

## Test Coverage Goals

- [ ] Backend unit tests: 80%+ coverage
- [ ] Backend integration tests: All API endpoints tested
- [ ] Frontend unit tests: Core components tested
- [ ] E2E tests: Critical user flows tested
