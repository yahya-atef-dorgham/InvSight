# ChainSight Local Development Startup Script for Windows
# This script starts all services locally for development

Write-Host "🚀 Starting ChainSight Local Development..." -ForegroundColor Cyan
Write-Host "===========================================" -ForegroundColor Cyan

# Check if Docker is available for database
$useDocker = $false
try {
    docker --version | Out-Null
    $useDocker = $true
    Write-Host "✓ Docker detected - will use Docker for database/Redis" -ForegroundColor Green
} catch {
    Write-Host "⚠ Docker not found - assuming PostgreSQL is installed locally" -ForegroundColor Yellow
}

# Start PostgreSQL and Redis if Docker is available
if ($useDocker) {
    Write-Host ""
    Write-Host "📦 Starting database services..." -ForegroundColor Cyan
    docker-compose up -d postgres redis
    Start-Sleep -Seconds 3
}

# Function to setup and start a Python service
function Start-PythonService {
    param(
        [string]$ServiceDir,
        [string]$ServiceName,
        [int]$Port
    )
    
    $fullPath = Join-Path $PSScriptRoot $ServiceDir
    
    if (-not (Test-Path $fullPath)) {
        Write-Host "❌ Directory not found: $ServiceDir" -ForegroundColor Red
        return
    }
    
    $venvPath = Join-Path $fullPath "venv"
    $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
    
    # Create virtual environment if it doesn't exist
    if (-not (Test-Path $venvPath)) {
        Write-Host "📦 Creating virtual environment for $ServiceName..." -ForegroundColor Yellow
        Set-Location $fullPath
        python -m venv venv
        & "$venvPath\Scripts\python.exe" -m pip install --upgrade pip
        & "$venvPath\Scripts\pip.exe" install -r requirements.txt
        Set-Location $PSScriptRoot
    }
    
    # Prepare command
    $command = "cd '$fullPath'; .\venv\Scripts\Activate.ps1; "
    
    if ($ServiceDir -eq "backend") {
        $command += "alembic upgrade head; "
    }
    
    $command += "uvicorn src.main:app --reload --port $Port"
    
    # Start in new window
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $command
    Write-Host "✓ Started $ServiceName on port $Port" -ForegroundColor Green
}

# Function to setup and start frontend
function Start-Frontend {
    $frontendPath = Join-Path $PSScriptRoot "frontend"
    
    if (-not (Test-Path $frontendPath)) {
        Write-Host "❌ Frontend directory not found" -ForegroundColor Red
        return
    }
    
    $nodeModulesPath = Join-Path $frontendPath "node_modules"
    
    # Install dependencies if needed
    if (-not (Test-Path $nodeModulesPath)) {
        Write-Host "📦 Installing frontend dependencies..." -ForegroundColor Yellow
        Set-Location $frontendPath
        npm install
        Set-Location $PSScriptRoot
    }
    
    # Start frontend
    $command = "cd '$frontendPath'; npm start"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $command
    Write-Host "✓ Started Frontend on port 3000" -ForegroundColor Green
}

# Start all services
Write-Host ""
Write-Host "🔨 Starting services..." -ForegroundColor Cyan

Start-PythonService -ServiceDir "backend" -ServiceName "Backend" -Port 8000
Start-Sleep -Seconds 2

Start-PythonService -ServiceDir "ai-service" -ServiceName "AI Service" -Port 8001
Start-Sleep -Seconds 2

Start-PythonService -ServiceDir "voice-service" -ServiceName "Voice Service" -Port 8002
Start-Sleep -Seconds 2

Start-Frontend

Write-Host ""
Write-Host "✅ All services are starting in separate windows!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Service URLs:" -ForegroundColor Cyan
Write-Host "   Frontend:     http://localhost:3000" -ForegroundColor Yellow
Write-Host "   Backend API:  http://localhost:8000" -ForegroundColor Yellow
Write-Host "   API Docs:     http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "   AI Service:   http://localhost:8001" -ForegroundColor Yellow
Write-Host "   Voice Service: http://localhost:8002" -ForegroundColor Yellow
Write-Host ""
Write-Host "⏳ Wait a few seconds for services to start..." -ForegroundColor Cyan
Write-Host "💡 Close the PowerShell windows to stop services" -ForegroundColor Gray
