# Deployment Guide - ChainSight Inventory Management System

This guide covers multiple deployment options for the ChainSight application, including Docker Compose, cloud platforms, and manual deployment.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Configuration](#environment-configuration)
3. [Docker Compose Deployment](#docker-compose-deployment)
4. [Manual Deployment](#manual-deployment)
5. [Cloud Deployment](#cloud-deployment)
6. [Production Considerations](#production-considerations)
7. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Prerequisites

### Required Software
- **Docker** 20.10+ and **Docker Compose** 2.0+ (for containerized deployment)
- **Python** 3.11+ (for manual deployment)
- **Node.js** 18+ and **npm** 9+ (for frontend)
- **PostgreSQL** 15+ (or use Docker)
- **Redis** 7+ (optional, for caching/rate limiting)

### System Requirements
- **CPU**: 2+ cores recommended
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 20GB+ free space
- **Network**: Ports 3000, 8000, 8001, 8002, 5432, 6379 available

---

## Environment Configuration

### Backend Environment Variables

Create `backend/.env`:

```bash
# Database
DATABASE_URL=postgresql://inventory_user:inventory_password@localhost:5432/inventory_db

# Redis (optional)
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-change-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com

# Service URLs
AI_SERVICE_URL=http://localhost:8001
VOICE_SERVICE_URL=http://localhost:8002

# Logging
LOG_LEVEL=INFO
```

### Frontend Environment Variables

Create `frontend/.env`:

```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
REACT_APP_AI_SERVICE_URL=http://localhost:8001
REACT_APP_VOICE_SERVICE_URL=http://localhost:8002
```

### AI Service Environment Variables

Create `ai-service/.env`:

```bash
PORT=8001
LOG_LEVEL=INFO
```

### Voice Service Environment Variables

Create `voice-service/.env`:

```bash
PORT=8002
LOG_LEVEL=INFO
```

---

## Docker Compose Deployment

### Quick Start (Automated)

**Linux/macOS:**
```bash
chmod +x deploy.sh
./deploy.sh dev    # Development
./deploy.sh prod   # Production
```

**Windows PowerShell:**
```powershell
.\deploy.ps1 -Environment dev    # Development
.\deploy.ps1 -Environment prod   # Production
```

### Manual Deployment

1. **Clone and navigate to project root:**
   ```bash
   cd ChainSight_spec-kit
   ```

2. **Set environment variables:**
   ```bash
   # Linux/macOS
   export SECRET_KEY=$(openssl rand -hex 32)
   
   # Windows PowerShell
   $env:SECRET_KEY = [Convert]::ToBase64String((1..32 | ForEach-Object {Get-Random -Minimum 0 -Maximum 256}))
   ```

3. **Start all services:**
   ```bash
   # Development
   docker-compose up -d
   
   # Production
   docker-compose -f docker-compose.prod.yml up -d
   ```

4. **Run database migrations:**
   ```bash
   docker-compose exec backend alembic upgrade head
   ```

5. **Access services:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - AI Service: http://localhost:8001
   - Voice Service: http://localhost:8002
   - API Docs: http://localhost:8000/docs

### Docker Compose Configuration

The `docker-compose.yml` includes:
- **PostgreSQL**: Database with persistent volume
- **Redis**: Caching and rate limiting
- **Backend**: FastAPI application
- **AI Service**: Forecasting and recommendations
- **Voice Service**: Voice processing
- **Frontend**: React application (add to docker-compose if needed)

### Customizing Docker Compose

Edit `docker-compose.yml` to:
- Change ports
- Add environment variables
- Configure volumes
- Set resource limits

---

## Manual Deployment

### Step 1: Database Setup

1. **Install PostgreSQL:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install postgresql-15

   # macOS
   brew install postgresql@15

   # Windows: Download from postgresql.org
   ```

2. **Create database and user:**
   ```sql
   CREATE DATABASE inventory_db;
   CREATE USER inventory_user WITH PASSWORD 'inventory_password';
   GRANT ALL PRIVILEGES ON DATABASE inventory_db TO inventory_user;
   ```

3. **Enable Row-Level Security (RLS):**
   ```sql
   \c inventory_db
   ALTER DATABASE inventory_db SET row_security = on;
   ```

### Step 2: Backend Deployment

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

6. **Start backend:**
   ```bash
   # Development
   uvicorn src.main:app --reload --port 8000

   # Production (with Gunicorn)
   gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

### Step 3: AI Service Deployment

1. **Navigate to AI service:**
   ```bash
   cd ai-service
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start service:**
   ```bash
   uvicorn src.main:app --host 0.0.0.0 --port 8001
   ```

### Step 4: Voice Service Deployment

1. **Navigate to voice service:**
   ```bash
   cd voice-service
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start service:**
   ```bash
   uvicorn src.main:app --host 0.0.0.0 --port 8002
   ```

### Step 5: Frontend Deployment

1. **Navigate to frontend:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Build for production:**
   ```bash
   npm run build
   ```

4. **Serve with a web server:**

   **Option A: Using serve (npm package):**
   ```bash
   npm install -g serve
   serve -s build -l 3000
   ```

   **Option B: Using nginx:**
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;
       
       root /path/to/frontend/build;
       index index.html;
       
       location / {
           try_files $uri $uri/ /index.html;
       }
       
       location /api {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

---

## Cloud Deployment

### AWS Deployment

#### Option 1: AWS ECS/Fargate

1. **Build Docker images:**
   ```bash
   docker build -t chainsight-backend ./backend
   docker build -t chainsight-ai-service ./ai-service
   docker build -t chainsight-voice-service ./voice-service
   ```

2. **Push to ECR:**
   ```bash
   aws ecr create-repository --repository-name chainsight-backend
   docker tag chainsight-backend:latest <account-id>.dkr.ecr.<region>.amazonaws.com/chainsight-backend:latest
   docker push <account-id>.dkr.ecr.<region>.amazonaws.com/chainsight-backend:latest
   ```

3. **Create ECS Task Definition** with:
   - Backend service
   - AI service
   - Voice service
   - RDS PostgreSQL instance
   - ElastiCache Redis

4. **Deploy frontend to S3 + CloudFront:**
   ```bash
   aws s3 sync frontend/build s3://your-bucket-name
   ```

#### Option 2: AWS Elastic Beanstalk

1. **Install EB CLI:**
   ```bash
   pip install awsebcli
   ```

2. **Initialize EB:**
   ```bash
   cd backend
   eb init -p python-3.11 chainsight-backend
   eb create chainsight-env
   ```

3. **Deploy:**
   ```bash
   eb deploy
   ```

### Google Cloud Platform (GCP)

#### Using Cloud Run

1. **Build and push images:**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/chainsight-backend ./backend
   ```

2. **Deploy to Cloud Run:**
   ```bash
   gcloud run deploy chainsight-backend \
     --image gcr.io/PROJECT_ID/chainsight-backend \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

3. **Use Cloud SQL for PostgreSQL**
4. **Use Cloud Memorystore for Redis**

### Azure Deployment

#### Using Azure Container Instances

1. **Build and push to Azure Container Registry:**
   ```bash
   az acr build --registry myregistry --image chainsight-backend ./backend
   ```

2. **Deploy container:**
   ```bash
   az container create \
     --resource-group myResourceGroup \
     --name chainsight-backend \
     --image myregistry.azurecr.io/chainsight-backend:latest \
     --dns-name-label chainsight-backend \
     --ports 8000
   ```

### Heroku Deployment

1. **Install Heroku CLI**

2. **Backend deployment:**
   ```bash
   cd backend
   heroku create chainsight-backend
   heroku addons:create heroku-postgresql:hobby-dev
   heroku addons:create heroku-redis:hobby-dev
   git push heroku main
   heroku run alembic upgrade head
   ```

3. **Frontend deployment:**
   ```bash
   cd frontend
   heroku create chainsight-frontend --buildpack https://github.com/mars/create-react-app-buildpack.git
   git push heroku main
   ```

### DigitalOcean App Platform

1. **Connect GitHub repository**
2. **Configure services:**
   - Backend: Python service
   - AI Service: Python service
   - Voice Service: Python service
   - Frontend: Static site
   - Database: Managed PostgreSQL
   - Redis: Managed Redis

---

## Production Considerations

### Security

1. **Change default secrets:**
   ```bash
   # Generate secure secret key
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Enable HTTPS:**
   - Use reverse proxy (nginx/Traefik)
   - Configure SSL certificates (Let's Encrypt)
   - Force HTTPS redirects

3. **Database security:**
   - Use strong passwords
   - Enable SSL connections
   - Restrict network access
   - Regular backups

4. **API security:**
   - Rate limiting enabled
   - CORS properly configured
   - Input validation
   - SQL injection prevention (SQLAlchemy ORM)

### Performance

1. **Database optimization:**
   - Add indexes (already in migrations)
   - Connection pooling
   - Query optimization

2. **Caching:**
   - Redis for frequently accessed data
   - Frontend caching headers

3. **Load balancing:**
   - Multiple backend instances
   - Nginx/HAProxy load balancer

4. **CDN for frontend:**
   - CloudFront/Cloudflare
   - Static asset optimization

### Monitoring

1. **Application monitoring:**
   - Log aggregation (ELK, CloudWatch)
   - Error tracking (Sentry)
   - Performance monitoring (New Relic, Datadog)

2. **Infrastructure monitoring:**
   - CPU, memory, disk usage
   - Database performance
   - Network latency

3. **Health checks:**
   - `/health` endpoints
   - Database connectivity
   - Service dependencies

### Backup & Recovery

1. **Database backups:**
   ```bash
   # Automated daily backups
   pg_dump -U inventory_user inventory_db > backup_$(date +%Y%m%d).sql
   ```

2. **Backup retention:**
   - Daily backups (7 days)
   - Weekly backups (4 weeks)
   - Monthly backups (12 months)

3. **Disaster recovery plan:**
   - Document recovery procedures
   - Test restore process
   - RTO/RPO targets

---

## Monitoring & Maintenance

### Health Check Endpoints

- Backend: `GET http://localhost:8000/health`
- AI Service: `GET http://localhost:8001/health`
- Voice Service: `GET http://localhost:8002/health`

### Log Management

1. **View logs:**
   ```bash
   # Docker Compose
   docker-compose logs -f backend

   # Manual deployment
   tail -f backend/logs/app.log
   ```

2. **Log rotation:**
   - Configure logrotate
   - Set retention policies

### Database Maintenance

1. **Run migrations:**
   ```bash
   alembic upgrade head
   ```

2. **Check database size:**
   ```sql
   SELECT pg_size_pretty(pg_database_size('inventory_db'));
   ```

3. **Vacuum and analyze:**
   ```sql
   VACUUM ANALYZE;
   ```

### Scaling

1. **Horizontal scaling:**
   - Add more backend instances
   - Use load balancer
   - Database read replicas

2. **Vertical scaling:**
   - Increase CPU/RAM
   - Optimize database queries
   - Add caching layers

---

## Troubleshooting

### Common Issues

1. **Database connection errors:**
   - Check DATABASE_URL
   - Verify PostgreSQL is running
   - Check firewall rules

2. **CORS errors:**
   - Update CORS_ORIGINS in settings
   - Verify frontend URL matches

3. **Service communication errors:**
   - Check service URLs in environment
   - Verify all services are running
   - Check network connectivity

4. **Migration errors:**
   - Check database permissions
   - Verify migration files
   - Review Alembic version history

### Getting Help

- Check logs for error messages
- Review `TESTING.md` for test procedures
- Consult `TEST_CHECKLIST.md` for verification steps

---

## Quick Reference

### Service Ports
- Frontend: 3000
- Backend: 8000
- AI Service: 8001
- Voice Service: 8002
- PostgreSQL: 5432
- Redis: 6379

### Key Commands

```bash
# Start all services (Docker)
docker-compose up -d

# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose exec backend alembic upgrade head

# View logs
docker-compose logs -f backend
docker-compose logs -f ai-service
docker-compose logs -f voice-service

# Stop all services
docker-compose down

# Rebuild containers
docker-compose up -d --build

# Check service health
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
```

---

## Next Steps

1. Configure production environment variables
2. Set up SSL certificates
3. Configure monitoring and alerts
4. Set up automated backups
5. Load test the application
6. Document runbooks for operations team

For more details, see:
- `TESTING.md` - Testing procedures
- `TEST_CHECKLIST.md` - Verification checklist
- `TEST_SUMMARY.md` - Implementation summary
