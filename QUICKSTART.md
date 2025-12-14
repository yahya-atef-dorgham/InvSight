# Quick Start - Run Locally

The fastest way to get ChainSight running on your local machine.

## 🚀 One-Command Start (Windows)

```powershell
.\start-local.ps1
```

## 🚀 One-Command Start (Linux/macOS)

```bash
chmod +x start-local.sh
./start-local.sh
```

## 📋 What the Script Does

1. ✅ Starts PostgreSQL and Redis (via Docker)
2. ✅ Creates Python virtual environments
3. ✅ Installs all dependencies
4. ✅ Runs database migrations
5. ✅ Starts all 4 services (Backend, AI Service, Voice Service, Frontend)

## 🌐 Access the Application

After running the script, wait 10-15 seconds, then open:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🛑 Stop Services

**Windows:** Close the PowerShell windows that opened

**Linux/macOS:**
```bash
pkill -f 'uvicorn|react-scripts'
```

## ⚙️ Manual Setup (If Script Doesn't Work)

### 1. Start Database (Docker)
```bash
docker-compose up -d postgres redis
```

### 2. Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
alembic upgrade head
uvicorn src.main:app --reload --port 8000
```

### 3. AI Service (New Terminal)
```bash
cd ai-service
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8001
```

### 4. Voice Service (New Terminal)
```bash
cd voice-service
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8002
```

### 5. Frontend (New Terminal)
```bash
cd frontend
npm install
npm start
```

## ✅ Verify It's Working

Open these URLs in your browser:

1. http://localhost:8000/health → Should show `{"status":"healthy"}`
2. http://localhost:8001/health → Should show `{"status":"healthy","service":"ai-service"}`
3. http://localhost:8002/health → Should show `{"status":"healthy","service":"voice-service"}`
4. http://localhost:3000 → Should show the frontend application

## 🐛 Troubleshooting

### Port Already in Use
```powershell
# Windows - Find and kill process
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Database Connection Error
Make sure PostgreSQL is running:
```bash
docker-compose ps  # Check if postgres container is running
```

### Python Not Found
- Windows: Use `py` instead of `python`
- Make sure Python 3.11+ is installed

### Module Not Found
Activate virtual environment:
```bash
# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

## 📚 More Information

- See `LOCAL_DEVELOPMENT.md` for detailed setup instructions
- See `DEPLOYMENT.md` for production deployment
- See `TESTING.md` for testing procedures
