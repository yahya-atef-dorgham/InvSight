#!/bin/bash

# ChainSight Local Development Startup Script for Linux/macOS
# This script starts all services locally for development

echo "🚀 Starting ChainSight Local Development..."
echo "==========================================="

# Check if Docker is available for database
if command -v docker &> /dev/null; then
    echo "✓ Docker detected - will use Docker for database/Redis"
    USE_DOCKER=true
else
    echo "⚠ Docker not found - assuming PostgreSQL is installed locally"
    USE_DOCKER=false
fi

# Start PostgreSQL and Redis if Docker is available
if [ "$USE_DOCKER" = true ]; then
    echo ""
    echo "📦 Starting database services..."
    docker-compose up -d postgres redis
    sleep 3
fi

# Function to setup and start a Python service
start_python_service() {
    local service_dir=$1
    local service_name=$2
    local port=$3
    
    if [ ! -d "$service_dir" ]; then
        echo "❌ Directory not found: $service_dir"
        return
    fi
    
    cd "$service_dir"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment for $service_name..."
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
    else
        source venv/bin/activate
    fi
    
    # Run migrations for backend
    if [ "$service_dir" = "backend" ]; then
        alembic upgrade head
    fi
    
    # Start service in background
    uvicorn src.main:app --reload --port "$port" > "../${service_dir}.log" 2>&1 &
    echo "✓ Started $service_name on port $port (PID: $!)"
    
    cd ..
}

# Function to setup and start frontend
start_frontend() {
    if [ ! -d "frontend" ]; then
        echo "❌ Frontend directory not found"
        return
    fi
    
    cd frontend
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo "📦 Installing frontend dependencies..."
        npm install
    fi
    
    # Start frontend in background
    npm start > "../frontend.log" 2>&1 &
    echo "✓ Started Frontend on port 3000 (PID: $!)"
    
    cd ..
}

# Start all services
echo ""
echo "🔨 Starting services..."

start_python_service "backend" "Backend" 8000
sleep 2

start_python_service "ai-service" "AI Service" 8001
sleep 2

start_python_service "voice-service" "Voice Service" 8002
sleep 2

start_frontend

echo ""
echo "✅ All services are starting!"
echo ""
echo "📍 Service URLs:"
echo "   Frontend:     http://localhost:3000"
echo "   Backend API:  http://localhost:8000"
echo "   API Docs:     http://localhost:8000/docs"
echo "   AI Service:   http://localhost:8001"
echo "   Voice Service: http://localhost:8002"
echo ""
echo "⏳ Wait a few seconds for services to start..."
echo "📋 Logs are saved to: backend.log, ai-service.log, voice-service.log, frontend.log"
echo ""
echo "🛑 To stop services, run: pkill -f 'uvicorn|react-scripts'"
