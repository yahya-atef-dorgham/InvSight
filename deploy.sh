#!/bin/bash

# ChainSight Deployment Script
# This script helps deploy the ChainSight application

set -e

echo "🚀 ChainSight Deployment Script"
echo "================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Determine which compose command to use
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

# Check environment
ENV=${1:-dev}

if [ "$ENV" = "prod" ]; then
    echo "📦 Deploying to PRODUCTION environment..."
    COMPOSE_FILE="docker-compose.prod.yml"
    
    # Check for required environment variables
    if [ -z "$SECRET_KEY" ]; then
        echo "⚠️  WARNING: SECRET_KEY not set. Generating one..."
        export SECRET_KEY=$(openssl rand -hex 32)
        echo "Generated SECRET_KEY: $SECRET_KEY"
        echo "⚠️  Please save this SECRET_KEY for future use!"
    fi
    
    if [ -z "$POSTGRES_PASSWORD" ]; then
        echo "❌ ERROR: POSTGRES_PASSWORD must be set for production"
        exit 1
    fi
else
    echo "📦 Deploying to DEVELOPMENT environment..."
    COMPOSE_FILE="docker-compose.yml"
fi

# Build and start services
echo ""
echo "🔨 Building Docker images..."
$COMPOSE_CMD -f $COMPOSE_FILE build

echo ""
echo "🚀 Starting services..."
$COMPOSE_CMD -f $COMPOSE_FILE up -d

# Wait for services to be healthy
echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Run database migrations
echo ""
echo "📊 Running database migrations..."
$COMPOSE_CMD -f $COMPOSE_FILE exec -T backend alembic upgrade head

# Check service health
echo ""
echo "🏥 Checking service health..."

BACKEND_HEALTH=$(curl -s http://localhost:8000/health || echo "unhealthy")
AI_HEALTH=$(curl -s http://localhost:8001/health || echo "unhealthy")
VOICE_HEALTH=$(curl -s http://localhost:8002/health || echo "unhealthy")

echo "Backend: $BACKEND_HEALTH"
echo "AI Service: $AI_HEALTH"
echo "Voice Service: $VOICE_HEALTH"

if [[ $BACKEND_HEALTH == *"healthy"* ]] && [[ $AI_HEALTH == *"healthy"* ]] && [[ $VOICE_HEALTH == *"healthy"* ]]; then
    echo ""
    echo "✅ All services are healthy!"
    echo ""
    echo "📍 Service URLs:"
    echo "   Frontend: http://localhost:3000"
    echo "   Backend API: http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
    echo "   AI Service: http://localhost:8001"
    echo "   Voice Service: http://localhost:8002"
    echo ""
    echo "🎉 Deployment complete!"
else
    echo ""
    echo "⚠️  Some services may not be healthy. Check logs:"
    echo "   $COMPOSE_CMD -f $COMPOSE_FILE logs"
    exit 1
fi
