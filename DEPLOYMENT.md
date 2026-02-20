# 🚀 DEPLOYMENT GUIDE
# EV Charging Diagnostic Chatbot Platform

## Quick Start (Development)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup MongoDB
**Option A: Local MongoDB**
```bash
# Install MongoDB from https://www.mongodb.com/try/download/community
# Start MongoDB service
mongod --dbpath /path/to/data
```

**Option B: MongoDB Atlas (Cloud)**
1. Create free account at https://www.mongodb.com/cloud/atlas
2. Create cluster
3. Get connection string
4. Update MONGODB_URL in .env

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings
```

### 4. Run Application
```bash
python run.py
```

Visit: http://localhost:8000/docs

---

## Production Deployment

### 🎨 Render Deployment (Recommended)

Render is the easiest way to deploy this chatbot with automatic HTTPS, free SSL, and continuous deployment.

#### Method 1: Using render.yaml (Recommended)

**Prerequisites:**
- GitHub/GitLab account with your code pushed
- MongoDB Atlas account (free tier available)

**Steps:**

1. **Setup MongoDB Atlas (if not already done)**
   ```
   - Go to https://www.mongodb.com/cloud/atlas
   - Create free cluster
   - Create database user
   - Whitelist all IPs (0.0.0.0/0) under Network Access
   - Get connection string (looks like: mongodb+srv://user:pass@cluster.mongodb.net/)
   ```

2. **Update render.yaml**
   - Open `render.yaml` in your project
   - Replace the `MONGODB_URL` value with your MongoDB Atlas connection string
   
3. **Deploy to Render**
   ```
   - Go to https://dashboard.render.com
   - Click "New +" → "Blueprint"
   - Connect your GitHub/GitLab repository
   - Render will auto-detect render.yaml
   - Click "Apply"
   - Wait for deployment (3-5 minutes)
   ```

4. **Your API is live!**
   ```
   - Access at: https://ecoplug-chatbot-api.onrender.com
   - API docs: https://ecoplug-chatbot-api.onrender.com/docs
   - Health check: https://ecoplug-chatbot-api.onrender.com/v1/health
   ```

#### Method 2: Manual Setup (Alternative)

**Steps:**

1. **Create Web Service**
   ```
   - Go to Render Dashboard
   - Click "New +" → "Web Service"
   - Connect your repository
   - Configure:
     * Name: ecoplug-chatbot-api
     * Runtime: Python 3
     * Build Command: pip install -r requirements.txt
     * Start Command: uvicorn chatbot.api.main:app --host 0.0.0.0 --port $PORT
   ```

2. **Add Environment Variables**
   ```
   In Render Dashboard → Environment tab, add:
   
   MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/ev_chatbot_db
   APP_NAME=EV Charging Diagnostic Chatbot
   DEBUG=false
   LOG_LEVEL=INFO
   ERROR_CODES_PATH=error_codes_complete.json
   FLOWS_PATH=chatbot/flows/chatbot_flows.json
   ```

3. **Deploy**
   ```
   - Click "Create Web Service"
   - Render will build and deploy automatically
   - Monitor logs in real-time
   ```

#### Post-Deployment

**Test Your API:**
```bash
# Health check
curl https://your-app.onrender.com/v1/health

# Start chat session
curl -X POST https://your-app.onrender.com/v1/chat/sessions \
  -H "Content-Type: application/json" \
  -d '{"metadata": {"platform": "web"}}'

# Send message
curl -X POST https://your-app.onrender.com/v1/chat/sessions/SESSION_ID/messages \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

**Update CORS (if needed):**
- If you have a frontend, update `CORS_ORIGINS` in environment variables
- Example: `CORS_ORIGINS=["https://myapp.com","https://www.myapp.com"]`

**Monitor Your App:**
- View logs: Render Dashboard → Logs tab
- Metrics: Dashboard shows CPU, Memory usage
- Auto-deploy: Enabled by default on git push

**Free Tier Notes:**
- ✅ Free tier includes 750 hours/month
- ⚠️ Services spin down after 15 min of inactivity
- ⚠️ First request after sleep takes ~30 seconds
- 💡 Upgrade to paid plan ($7/mo) for always-on service

---

### Docker Deployment

**1. Create Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY chatbot/ ./chatbot/
COPY error_codes_complete.json .
COPY .env .

# Run application
CMD ["uvicorn", "chatbot.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**2. Build and Run**
```bash
docker build -t ev-chatbot .
docker run -p 8000:8000 -e MONGODB_URL=your_mongo_url ev-chatbot
```

**3. Docker Compose (with MongoDB)**
```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:7
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: password

  chatbot:
    build: .
    ports:
      - "8000:8000"
    environment:
      MONGODB_URL: mongodb://admin:password@mongodb:27017/
      LOG_LEVEL: INFO
      DEBUG: "False"
    depends_on:
      - mongodb

volumes:
  mongo_data:
```

Run: `docker-compose up -d`

---

### Cloud Deployment Options

#### ☁️ AWS Deployment

**Option 1: AWS Elastic Beanstalk**
1. Install AWS CLI and EB CLI
2. Initialize: `eb init`
3. Create environment: `eb create production`
4. Deploy: `eb deploy`

**Option 2: AWS ECS (Fargate)**
1. Push Docker image to ECR
2. Create ECS cluster
3. Define task definition
4. Create service with load balancer

**Option 3: AWS Lambda (Serverless)**
```bash
pip install mangum
# Add to main.py: handler = Mangum(app)
```

#### 🌐 Google Cloud Platform

**Cloud Run (Recommended)**
```bash
gcloud run deploy ev-chatbot \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

**App Engine**
Create `app.yaml`:
```yaml
runtime: python311
entrypoint: uvicorn chatbot.api.main:app --host 0.0.0.0 --port $PORT
```

Deploy: `gcloud app deploy`

#### 🔷 Azure

**Azure Container Apps**
```bash
az containerapp up \
  --name ev-chatbot \
  --resource-group myResourceGroup \
  --location eastus \
  --environment myEnvironment \
  --image myregistry.azurecr.io/ev-chatbot:latest
```

#### 🌊 Digital Ocean

**App Platform**
1. Connect GitHub repo
2. Auto-detect Dockerfile
3. Configure environment variables
4. Deploy

**Droplet**
```bash
# SSH into droplet
git clone <repo>
cd ecoplug_bot
pip install -r requirements.txt
# Use systemd or supervisor to run
```

#### ⚡ Heroku

Create `Procfile`:
```
web: uvicorn chatbot.api.main:app --host 0.0.0.0 --port $PORT
```

Deploy:
```bash
heroku create ev-chatbot
git push heroku main
```

---

## Environment Configuration

### Required Variables
```env
MONGODB_URL=mongodb://user:pass@host:27017/db
```

### Optional Variables
```env
# OpenAI Integration
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4

# Performance
MONGODB_MAX_CONNECTIONS=50
SESSION_TIMEOUT_MINUTES=60

# Security
CORS_ORIGINS=["https://yourdomain.com"]
RATE_LIMIT_PER_MINUTE=100

# Logging
LOG_LEVEL=WARNING
LOG_FORMAT=json
```

---

## Performance Tuning

### 1. Horizontal Scaling
Run multiple instances behind load balancer:
- AWS ELB / ALB
- NGINX
- HAProxy

### 2. Database Optimization
```javascript
// Indexes (auto-created by app)
db.chat_sessions.createIndex({ user_id: 1 })
db.chat_sessions.createIndex({ session_id: 1 }, { unique: true })
db.chat_sessions.createIndex({ updated_at: 1 }, { expireAfterSeconds: 86400 })

// Read preference for replicas
MongoClient(url, {
  readPreference: 'secondaryPreferred'
})
```

### 3. Caching
Add Redis for session caching:
```python
from redis import asyncio as aioredis

redis = await aioredis.from_url("redis://localhost")
```

### 4. CDN
Serve static assets via CloudFront/CloudFlare

---

## Monitoring & Logging

### Application Monitoring

**1. Health Checks**
- Endpoint: `/v1/health`
- Monitor: status, diagnostics_loaded, error_codes_count

**2. Structured Logging**
All logs output as JSON (LOG_FORMAT=json):
```json
{
  "timestamp": "2026-02-19T10:30:00Z",
  "level": "INFO",
  "message": "Diagnostic match found",
  "error_code": "ER001",
  "user_id": "user_123"
}
```

**3. Log Aggregation**
- **CloudWatch** (AWS)
- **Stackdriver** (GCP)
- **Application Insights** (Azure)
- **ELK Stack** (Self-hosted)
- **Datadog** (SaaS)

### Performance Metrics
Monitor:
- Response time per endpoint
- Error rate
- Active sessions count
- MongoDB query performance
- Memory/CPU usage

---

## Security Best Practices

### 1. Authentication
Add API key middleware:
```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key
```

### 2. Rate Limiting
```bash
pip install slowapi
```

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/v1/chat")
@limiter.limit("60/minute")
async def chat(...):
    ...
```

### 3. HTTPS Only
```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
app.add_middleware(HTTPSRedirectMiddleware)
```

### 4. Input Validation
Already implemented via Pydantic models

### 5. Secrets Management
- **AWS**: Secrets Manager
- **GCP**: Secret Manager
- **Azure**: Key Vault
- **HashiCorp**: Vault

---

## Backup & Recovery

### MongoDB Backup
```bash
# Backup
mongodump --uri="mongodb://user:pass@host/db" --out=/backup

# Restore
mongorestore --uri="mongodb://user:pass@host/db" /backup/db
```

### Automated Backups
- MongoDB Atlas: Auto-backups included
- AWS: Use AWS Backup
- Cron job: `0 2 * * * mongodump ...`

---

## Testing in Production

### Smoke Tests
```bash
curl https://your-domain.com/v1/health
```

### Load Testing
```bash
pip install locust

# Create locustfile.py
from locust import HttpUser, task

class ChatbotUser(HttpUser):
    @task
    def chat(self):
        self.client.post("/v1/chat", json={
            "user_id": "load_test",
            "message": "ER001",
            "platform": "web"
        })

# Run: locust -f locustfile.py
```

---

## Rollback Strategy

### Blue-Green Deployment
1. Deploy new version to separate environment
2. Test thoroughly
3. Switch traffic via load balancer
4. Keep old version running for quick rollback

### Database Migrations
```python
# Use Alembic or similar
alembic revision --autogenerate -m "Add new field"
alembic upgrade head
```

---

## Cost Optimization

### AWS
- Use t3.micro/t3.small for API
- RDS/DocumentDB reserved instances
- S3 for static assets
- CloudFront CDN

### GCP
- Cloud Run (pay per request)
- Cloud Storage
- MongoDB Atlas (M0 free tier for dev)

### Estimated Monthly Costs
- **Starter** (< 10K req/day): $20-50
- **Growth** (< 100K req/day): $100-300
- **Production** (< 1M req/day): $500-1500

---

## Troubleshooting

### Issue: Can't connect to MongoDB
```bash
# Check connection
mongosh "mongodb://localhost:27017"

# Check environment
echo $MONGODB_URL

# Check logs
docker logs <container-id>
```

### Issue: Diagnostic database not loading
- Verify `error_codes_complete.json` exists
- Check ERROR_CODES_PATH in .env
- Review startup logs

### Issue: 503 Service Unavailable
- Check health endpoint
- Verify all engines initialized
- Check MongoDB connection

---

## Support & Maintenance

### Regular Tasks
- [ ] Weekly: Review logs for errors
- [ ] Monthly: Update dependencies
- [ ] Quarterly: Security audit
- [ ] Yearly: Major version upgrades

### Dependency Updates
```bash
pip list --outdated
pip install --upgrade <package>
```

---

## Useful Commands

```bash
# Start development server
python run.py

# Run tests
python test_api.py

# Check dependencies
pip check

# Generate requirements
pip freeze > requirements.txt

# Database shell
mongosh "mongodb://localhost:27017/ev_chatbot_db"

# View logs
tail -f logs/app.log

# Check port usage
lsof -i :8000  # Unix
netstat -ano | findstr :8000  # Windows
```

---

## Additional Resources

- FastAPI Docs: https://fastapi.tiangolo.com
- MongoDB Docs: https://docs.mongodb.com
- OpenAI API: https://platform.openai.com/docs
- Pydantic: https://docs.pydantic.dev

---

**Need Help?**
- GitHub Issues
- Email: support@evcharging.com
- Documentation: /docs endpoint
