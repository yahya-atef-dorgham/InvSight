# ChainSight Deployment Script for Windows PowerShell
# This script helps deploy the ChainSight application

param(
    [string]$Environment = "dev"
)

Write-Host "🚀 ChainSight Deployment Script" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Check if Docker is installed
try {
    docker --version | Out-Null
} catch {
    Write-Host "❌ Docker is not installed. Please install Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Check if Docker Compose is available
try {
    docker compose version | Out-Null
    $ComposeCmd = "docker compose"
} catch {
    try {
        docker-compose --version | Out-Null
        $ComposeCmd = "docker-compose"
    } catch {
        Write-Host "❌ Docker Compose is not installed. Please install Docker Compose first." -ForegroundColor Red
        exit 1
    }
}

if ($Environment -eq "prod") {
    Write-Host "📦 Deploying to PRODUCTION environment..." -ForegroundColor Yellow
    $ComposeFile = "docker-compose.prod.yml"
    
    # Check for required environment variables
    if (-not $env:SECRET_KEY) {
        Write-Host "⚠️  WARNING: SECRET_KEY not set. Generating one..." -ForegroundColor Yellow
        $env:SECRET_KEY = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
        Write-Host "Generated SECRET_KEY: $($env:SECRET_KEY)" -ForegroundColor Yellow
        Write-Host "⚠️  Please save this SECRET_KEY for future use!" -ForegroundColor Yellow
    }
    
    if (-not $env:POSTGRES_PASSWORD) {
        Write-Host "❌ ERROR: POSTGRES_PASSWORD must be set for production" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "📦 Deploying to DEVELOPMENT environment..." -ForegroundColor Green
    $ComposeFile = "docker-compose.yml"
}

# Build and start services
Write-Host ""
Write-Host "🔨 Building Docker images..." -ForegroundColor Cyan
& $ComposeCmd.Split(' ') -f $ComposeFile build

Write-Host ""
Write-Host "🚀 Starting services..." -ForegroundColor Cyan
& $ComposeCmd.Split(' ') -f $ComposeFile up -d

# Wait for services to be healthy
Write-Host ""
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

# Run database migrations
Write-Host ""
Write-Host "📊 Running database migrations..." -ForegroundColor Cyan
& $ComposeCmd.Split(' ') -f $ComposeFile exec -T backend alembic upgrade head

# Check service health
Write-Host ""
Write-Host "🏥 Checking service health..." -ForegroundColor Cyan

try {
    $BackendHealth = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5
    Write-Host "Backend: $($BackendHealth.status)" -ForegroundColor Green
} catch {
    Write-Host "Backend: unhealthy" -ForegroundColor Red
}

try {
    $AIHealth = Invoke-RestMethod -Uri "http://localhost:8001/health" -TimeoutSec 5
    Write-Host "AI Service: $($AIHealth.status)" -ForegroundColor Green
} catch {
    Write-Host "AI Service: unhealthy" -ForegroundColor Red
}

try {
    $VoiceHealth = Invoke-RestMethod -Uri "http://localhost:8002/health" -TimeoutSec 5
    Write-Host "Voice Service: $($VoiceHealth.status)" -ForegroundColor Green
} catch {
    Write-Host "Voice Service: unhealthy" -ForegroundColor Red
}

Write-Host ""
Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Service URLs:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:3000"
Write-Host "   Backend API: http://localhost:8000"
Write-Host "   API Docs: http://localhost:8000/docs"
Write-Host "   AI Service: http://localhost:8001"
Write-Host "   Voice Service: http://localhost:8002"
