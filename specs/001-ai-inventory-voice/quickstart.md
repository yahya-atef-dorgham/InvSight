# Quick Start Guide: AI-Powered Inventory Management System

**Feature**: 001-ai-inventory-voice  
**Date**: 2025-01-27

## Overview

This guide helps developers get started with implementing the AI-Powered Inventory Management System. Follow these steps to set up the development environment and begin implementation.

## Prerequisites

- Python 3.11+ (backend, AI service, voice service)
- Node.js 20+ (frontend)
- PostgreSQL 15+ (database)
- Redis 7+ (caching, job queue)
- Docker and Docker Compose (for local development)
- Git

## Architecture Overview

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Frontend   │────▶│   Backend    │────▶│ PostgreSQL  │
│  (React)    │     │  (FastAPI)   │     │             │
└─────────────┘     └──────────────┘     └─────────────┘
                            │
                            ├────▶┌─────────────┐
                            │     │ AI Service  │
                            │     │  (Python)   │
                            │     └─────────────┘
                            │
                            └────▶┌─────────────┐
                                  │   Voice     │
                                  │  Service    │
                                  │  (Python)   │
                                  └─────────────┘
```

## Step 1: Repository Setup

### Clone and Branch Setup

```bash
git clone <repository-url>
cd ChainSight_spec-kit
git checkout 001-ai-inventory-voice
```

### Create Project Structure

```bash
# Backend
mkdir -p backend/src/{api/v1,models,services,database/migrations,config}
mkdir -p backend/tests/{unit,integration,contract}

# Frontend
mkdir -p frontend/src/{components/{common,inventory,products,warehouses,purchase-orders,voice},pages,services,stores,utils}
mkdir -p frontend/tests/{unit,integration,e2e}

# AI Service
mkdir -p ai-service/src/{models/{forecasting,nlp},services,training/pipelines,registry}
mkdir -p ai-service/tests/evaluation

# Voice Service
mkdir -p voice-service/src/{speech_to_text,text_to_speech,nlp_processor,api}
mkdir -p voice-service/tests
```

## Step 2: Backend Setup

### Initialize Python Project

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install fastapi uvicorn sqlalchemy alembic pydantic psycopg2-binary redis python-jose[cryptography] passlib[bcrypt] python-multipart websockets
pip install pytest pytest-asyncio httpx  # Testing
```

### Create `backend/requirements.txt`

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
pydantic==2.5.0
pydantic-settings==2.1.0
psycopg2-binary==2.9.9
redis==5.0.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
websockets==12.0
```

### Initialize Alembic (Database Migrations)

```bash
cd backend
alembic init alembic
# Edit alembic.ini to set sqlalchemy.url
# Edit alembic/env.py to import models
```

### Database Configuration

Create `backend/src/config/settings.py`:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    redis_url: str = "redis://localhost:6379"
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()
```

Create `backend/.env`:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/inventory_db
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-here
```

## Step 3: Database Setup

### Create Database

```bash
createdb inventory_db
```

### Run Initial Migration

```bash
cd backend
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

This creates all tables defined in `data-model.md`.

## Step 4: Frontend Setup

### Initialize React Project

```bash
cd frontend
npx create-react-app . --template typescript
npm install axios react-router-dom @tanstack/react-query
npm install --save-dev @testing-library/react @testing-library/jest-dom playwright
```

### Install UI Libraries (Salesforce Lightning Design System compatible)

```bash
npm install @salesforce-ux/design-system  # Or alternative: Lightning Design System React components
npm install recharts  # For dashboard charts
```

### Configure API Client

Create `frontend/src/services/api.ts`:

```typescript
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token interceptor
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

Create `frontend/.env`:

```env
REACT_APP_API_URL=http://localhost:8000/v1
```

## Step 5: Docker Compose (Local Development)

Create `docker-compose.yml` at repository root:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: inventory_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:password@postgres:5432/inventory_db
      REDIS_URL: redis://redis:6379
    depends_on:
      - postgres
      - redis
    volumes:
      - ./backend:/app

volumes:
  postgres_data:
  redis_data:
```

Start services:

```bash
docker-compose up -d
```

## Step 6: Implement Core Features (Phase 1)

### 6.1 Create Base Models

Create `backend/src/models/base.py`:

```python
from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid

class BaseModel:
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

### 6.2 Implement Product Model

Create `backend/src/models/product.py` (see `data-model.md` for full schema):

```python
from sqlalchemy import Column, String, Text
from .base import BaseModel
from database.session import Base

class Product(BaseModel, Base):
    __tablename__ = 'products'
    
    sku = Column(String(100), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    unit_of_measure = Column(String(50), nullable=False)
```

### 6.3 Create API Endpoints

Create `backend/src/api/v1/products.py`:

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.product import Product
from database.session import get_db

router = APIRouter(prefix="/products", tags=["products"])

@router.get("")
async def list_products(
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db)
):
    # Implementation here
    pass

@router.post("")
async def create_product(
    product_data: dict,
    db: Session = Depends(get_db)
):
    # Implementation here
    pass
```

### 6.4 Create Main Application

Create `backend/src/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1 import products

app = FastAPI(title="Inventory Management API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router, prefix="/v1")

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

### 6.5 Run Backend

```bash
cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 6.6 Create Frontend Components

Create `frontend/src/pages/Products/ProductsList.tsx`:

```typescript
import React, { useEffect, useState } from 'react';
import { apiClient } from '../../services/api';

interface Product {
  id: string;
  sku: string;
  name: string;
  category?: string;
}

export const ProductsList: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);

  useEffect(() => {
    apiClient.get('/products')
      .then(response => setProducts(response.data.items))
      .catch(error => console.error(error));
  }, []);

  return (
    <div>
      <h1>Products</h1>
      <table>
        <thead>
          <tr>
            <th>SKU</th>
            <th>Name</th>
            <th>Category</th>
          </tr>
        </thead>
        <tbody>
          {products.map(product => (
            <tr key={product.id}>
              <td>{product.sku}</td>
              <td>{product.name}</td>
              <td>{product.category}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
```

### 6.7 Run Frontend

```bash
cd frontend
npm start
```

Frontend will be available at http://localhost:3000

## Step 7: Implement Authentication

### 7.1 Create Auth Middleware

Create `backend/src/api/middleware/auth.py`:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from config.settings import settings

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        tenant_id = payload.get("tenant_id")
        user_id = payload.get("sub")
        roles = payload.get("roles", [])
        if tenant_id is None or user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"user_id": user_id, "tenant_id": tenant_id, "roles": roles}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### 7.2 Add Tenant Middleware

Create `backend/src/api/middleware/tenant.py`:

```python
from fastapi import Depends
from api.middleware.auth import get_current_user

def get_tenant_id(current_user: dict = Depends(get_current_user)):
    return current_user["tenant_id"]
```

Use in endpoints:

```python
@router.get("")
async def list_products(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    # All queries filtered by tenant_id
    pass
```

## Step 8: Testing

### 8.1 Write Unit Tests

Create `backend/tests/unit/test_products.py`:

```python
import pytest
from models.product import Product

def test_product_creation():
    product = Product(
        tenant_id="123e4567-e89b-12d3-a456-426614174000",
        sku="TEST-001",
        name="Test Product",
        unit_of_measure="pieces"
    )
    assert product.sku == "TEST-001"
    assert product.name == "Test Product"
```

### 8.2 Run Tests

```bash
cd backend
pytest tests/ -v
```

## Step 9: Next Steps

1. **Implement remaining models**: Inventory, Warehouse, PurchaseOrder, etc. (see `data-model.md`)
2. **Implement inventory movements**: Follow Phase 2 in `plan.md`
3. **Add real-time updates**: WebSocket implementation for dashboard
4. **Integrate AI service**: Connect to forecast generation (Phase 3)
5. **Add voice service**: Implement voice query endpoints (Phase 5)

## Development Workflow

1. **Write tests first** (TDD required by Constitution)
2. **Implement feature** (make tests pass)
3. **Run linters and formatters**:
   ```bash
   # Backend
   ruff check backend/src
   black backend/src
   
   # Frontend
   npm run lint
   npm run format
   ```
4. **Run test suite**:
   ```bash
   pytest backend/tests
   npm test frontend
   ```
5. **Commit changes** (ensure 80% code coverage)

## Useful Commands

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### API Documentation

Once backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Testing

```bash
# Backend unit tests
pytest backend/tests/unit

# Backend integration tests
pytest backend/tests/integration

# Frontend unit tests
cd frontend && npm test

# E2E tests
cd frontend && npx playwright test
```

## Resources

- **Specification**: `spec.md`
- **Implementation Plan**: `plan.md`
- **Data Model**: `data-model.md`
- **API Contracts**: `contracts/openapi.yaml`
- **Research**: `research.md`
- **Constitution**: `.specify/memory/constitution.md`

## Getting Help

- Review the specification for requirements
- Check API contracts in `contracts/openapi.yaml`
- Refer to research document for technology decisions
- Follow Constitution principles for architecture patterns

