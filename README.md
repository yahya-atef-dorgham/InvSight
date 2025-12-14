# ChainSight - AI-Powered Inventory Management System

A comprehensive inventory management system with AI-driven forecasting, voice interaction, and real-time updates.

## 🚀 Features

- **Real-Time Inventory Dashboard** - Live inventory tracking with WebSocket updates
- **Inventory Movements** - Track inbound, outbound, and transfer movements
- **AI-Powered Forecasting** - Demand prediction using time-series analysis
- **Smart Recommendations** - AI-generated reorder suggestions with explanations
- **Purchase Order Management** - Complete PO workflow with state machine
- **Voice Assistant** - Natural language queries using Web Speech API
- **Multi-Tenancy** - Row-level security for data isolation
- **Audit Logging** - Complete audit trail for all operations

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ (or Docker)
- Docker (optional, for database)

## 🏃 Quick Start

### Windows
```powershell
.\start-local.ps1
```

### Linux/macOS
```bash
chmod +x start-local.sh
./start-local.sh
```

See [QUICKSTART.md](QUICKSTART.md) for detailed instructions.

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
- **[LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md)** - Detailed local setup guide
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide
- **[TESTING.md](TESTING.md)** - Testing procedures
- **[TEST_CHECKLIST.md](TEST_CHECKLIST.md)** - Test verification checklist

## 🏗️ Architecture

- **Backend**: FastAPI (Python) - REST API and WebSocket server
- **Frontend**: React + TypeScript - Modern SPA with real-time updates
- **AI Service**: FastAPI (Python) - Forecasting and recommendation engine
- **Voice Service**: FastAPI (Python) - Speech processing and NLP
- **Database**: PostgreSQL with Row-Level Security
- **Cache**: Redis (optional)

## 🛠️ Tech Stack

### Backend
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- JWT Authentication
- WebSockets

### Frontend
- React 18
- TypeScript
- React Query
- React Router
- Web Speech API
- Recharts

### AI/Voice Services
- FastAPI
- Scikit-learn
- NLP processing
- Model versioning

## 📦 Project Structure

```
ChainSight_spec-kit/
├── backend/          # Main API server
├── frontend/         # React application
├── ai-service/       # AI forecasting service
├── voice-service/    # Voice processing service
├── specs/            # Project specifications
└── docker-compose.yml
```

## 🔧 Development

1. **Start database:**
   ```bash
   docker-compose up -d postgres redis
   ```

2. **Run migrations:**
   ```bash
   cd backend
   alembic upgrade head
   ```

3. **Start services:**
   - Backend: `uvicorn src.main:app --reload --port 8000`
   - AI Service: `uvicorn src.main:app --reload --port 8001`
   - Voice Service: `uvicorn src.main:app --reload --port 8002`
   - Frontend: `npm start`

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm test
```

## 📝 API Documentation

Once running, access API docs at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔐 Security

- JWT-based authentication
- Row-Level Security (RLS) for multi-tenancy
- Rate limiting
- Security headers
- Input validation and sanitization

## 📄 License

[Add your license here]

## 🤝 Contributing

[Add contribution guidelines]

## 📞 Support

[Add support information]
