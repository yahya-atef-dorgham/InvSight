# Local Development Guide

Quick guide to run ChainSight locally on your machine.

## Prerequisites

- **Python 3.11+** installed
- **Node.js 18+** and **npm** installed
- **PostgreSQL 15+** (or use Docker for database only)
- **Git** (to clone the repository)

## Quick Start (Recommended)

### Option 1: Using Docker Compose (Easiest)

1. **Start database and Redis:**
   ```bash
   docker-compose up -d postgres redis
   ```

2. **Set up Python virtual environments and install dependencies:**
   ```bash
   # Backend
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cd ..
   
   # AI Service
   cd ai-service
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cd ..
   
   # Voice Service
   cd voice-service
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cd ..
   ```

3. **Run database migrations:**
   ```bash
   cd backend
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   alembic upgrade head
   cd ..
   ```

4. **Start all services in separate terminals:**

   **Terminal 1 - Backend:**
   ```bash
   cd backend
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   uvicorn src.main:app --reload --port 8000
   ```

   **Terminal 2 - AI Service:**
   ```bash
   cd ai-service
   source venv/bin/activate
   uvicorn src.main:app --reload --port 8001
   ```

   **Terminal 3 - Voice Service:**
   ```bash
   cd voice-service
   source venv/bin/activate
   uvicorn src.main:app --reload --port 8002
   ```

   **Terminal 4 - Frontend:**
   ```bash
   cd frontend
   npm install
   npm start
   ```

5. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - AI Service: http://localhost:8001
   - Voice Service: http://localhost:8002

### Option 2: Full Docker Compose (All Services)

If you prefer everything in Docker:

```bash
# Start all services
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head

# View logs
docker-compose logs -f
```

---

## Manual Setup (Without Docker)

### Step 1: Install PostgreSQL

**Windows:**
- Download from https://www.postgresql.org/download/windows/
- Install and start PostgreSQL service

**macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install postgresql-15
sudo systemctl start postgresql
```

### Step 2: Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Run these SQL commands:
CREATE DATABASE inventory_db;
CREATE USER inventory_user WITH PASSWORD 'inventory_password';
GRANT ALL PRIVILEGES ON DATABASE inventory_db TO inventory_user;
\q
```

### Step 3: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (optional, defaults work for local dev)
# DATABASE_URL=postgresql://inventory_user:inventory_password@localhost:5432/inventory_db

# Run migrations
alembic upgrade head

# Start backend
uvicorn src.main:app --reload --port 8000
```

### Step 4: AI Service Setup

```bash
cd ai-service

# Create virtual environment
python -m venv venv

# Activate
# Windows: venv\Scripts\activate
# Linux/macOS: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start service
uvicorn src.main:app --reload --port 8001
```

### Step 5: Voice Service Setup

```bash
cd voice-service

# Create virtual environment
python -m venv venv

# Activate
# Windows: venv\Scripts\activate
# Linux/macOS: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start service
uvicorn src.main:app --reload --port 8002
```

### Step 6: Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

---

## Quick Start Scripts

### Windows PowerShell

Create `start-local.ps1`:

```powershell
# Start all services locally
Write-Host "Starting ChainSight Local Development..." -ForegroundColor Cyan

# Start PostgreSQL and Redis (if using Docker)
docker-compose up -d postgres redis

# Backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; if (Test-Path venv) { .\venv\Scripts\activate } else { python -m venv venv; .\venv\Scripts\activate; pip install -r requirements.txt }; alembic upgrade head; uvicorn src.main:app --reload --port 8000"

# AI Service
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd ai-service; if (Test-Path venv) { .\venv\Scripts\activate } else { python -m venv venv; .\venv\Scripts\activate; pip install -r requirements.txt }; uvicorn src.main:app --reload --port 8001"

# Voice Service
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd voice-service; if (Test-Path venv) { .\venv\Scripts\activate } else { python -m venv venv; .\venv\Scripts\activate; pip install -r requirements.txt }; uvicorn src.main:app --reload --port 8002"

# Frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; if (-not (Test-Path node_modules)) { npm install }; npm start"

Write-Host "All services starting in separate windows..." -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Yellow
Write-Host "Backend: http://localhost:8000" -ForegroundColor Yellow
```

### Linux/macOS

Create `start-local.sh`:

```bash
#!/bin/bash

echo "Starting ChainSight Local Development..."

# Start PostgreSQL and Redis (if using Docker)
docker-compose up -d postgres redis

# Function to start service in background
start_service() {
    local dir=$1
    local port=$2
    local name=$3
    
    cd "$dir"
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    else
        source venv/bin/activate
    fi
    
    if [ "$dir" = "backend" ]; then
        alembic upgrade head
    fi
    
    uvicorn src.main:app --reload --port "$port" &
    echo "Started $name on port $port"
    cd ..
}

# Start services
start_service backend 8000 "Backend"
start_service ai-service 8001 "AI Service"
start_service voice-service 8002 "Voice Service"

# Frontend
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
fi
npm start &
cd ..

echo ""
echo "✅ All services starting..."
echo "Frontend: http://localhost:3000"
echo "Backend: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
```

---

## Environment Variables

### Backend (.env file in backend/)

```bash
DATABASE_URL=postgresql://inventory_user:inventory_password@localhost:5432/inventory_db
REDIS_URL=redis://localhost:6379
SECRET_KEY=dev-secret-key-change-in-production
AI_SERVICE_URL=http://localhost:8001
VOICE_SERVICE_URL=http://localhost:8002
CORS_ORIGINS=http://localhost:3000
```

### Frontend (.env file in frontend/)

```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

---

## Verifying Setup

1. **Check backend:**
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status":"healthy"}
   ```

2. **Check AI service:**
   ```bash
   curl http://localhost:8001/health
   # Should return: {"status":"healthy","service":"ai-service"}
   ```

3. **Check voice service:**
   ```bash
   curl http://localhost:8002/health
   # Should return: {"status":"healthy","service":"voice-service"}
   ```

4. **Open frontend:**
   - Navigate to http://localhost:3000
   - Should see the login page or dashboard

---

## Common Issues

### Port Already in Use

If a port is already in use:

```bash
# Find process using port (Windows)
netstat -ano | findstr :8000

# Find process using port (Linux/macOS)
lsof -i :8000

# Kill process (replace PID with actual process ID)
# Windows:
taskkill /PID <PID> /F
# Linux/macOS:
kill -9 <PID>
```

### Database Connection Error

1. Check PostgreSQL is running:
   ```bash
   # Windows
   Get-Service postgresql*
   
   # Linux/macOS
   sudo systemctl status postgresql
   ```

2. Verify connection:
   ```bash
   psql -U inventory_user -d inventory_db -h localhost
   ```

3. Check DATABASE_URL in backend/.env

### Module Not Found Errors

1. Ensure virtual environment is activated
2. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Frontend Build Errors

1. Clear node_modules and reinstall:
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

---

## Development Workflow

1. **Make code changes** - Services auto-reload (except frontend, which hot-reloads)
2. **Run tests:**
   ```bash
   # Backend tests
   cd backend
   pytest tests/ -v
   
   # Frontend tests
   cd frontend
   npm test
   ```
3. **Check logs** in terminal windows
4. **Access API docs** at http://localhost:8000/docs

---

## Stopping Services

- **Ctrl+C** in each terminal window
- **Or use Docker Compose:**
  ```bash
  docker-compose down
  ```

---

## Next Steps

- Read `DEPLOYMENT.md` for production deployment
- Check `TESTING.md` for testing procedures
- Review `TEST_CHECKLIST.md` for verification steps
