# Deployment Guide - StoreVision Analytics Platform

This guide covers deploying StoreVision to various platforms.

## Local Deployment

### Windows

1. Clone repository
2. Create virtual environment: `python -m venv venv`
3. Activate: `venv\Scripts\activate`
4. Install dependencies: `pip install -r backend/requirements.txt`
5. Run: `python backend/main.py`
6. Access: http://localhost:8000

### Linux/Mac

```bash
git clone <repo-url>
cd storevision-analytics
python3 -m venv venv
source venv/bin/activate
cd backend
pip install -r requirements.txt
python main.py
```

Access: http://localhost:8000

## Docker Deployment

### Local Docker

```bash
docker-compose up --build
```

Access: http://localhost:8000

### Docker Hub

1. Build image:
```bash
docker build -t yourusername/storevision:latest .
```

2. Push to Docker Hub:
```bash
docker push yourusername/storevision:latest
```

3. Run from Docker Hub:
```bash
docker run -p 8000:8000 yourusername/storevision:latest
```

## Cloud Deployment

### Heroku

1. Install Heroku CLI
2. Create Heroku app: `heroku create your-app-name`
3. Add Procfile with: `web: cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Deploy: `git push heroku main`

### AWS Elastic Container Service

1. Push image to ECR
2. Create ECS task definition
3. Deploy to ECS cluster
4. Configure load balancer

### Google Cloud Run

```bash
gcloud run deploy storevision \
  --source . \
  --platform managed \
  --region us-central1
```

### DigitalOcean App Platform

1. Connect GitHub repository
2. Configure build command: `pip install -r backend/requirements.txt`
3. Configure run command: `cd backend && uvicorn main:app --host 0.0.0.0 --port 8080`
4. Deploy

## Environment Variables

Create `.env` file in backend directory:

```
PYTHONUNBUFFERED=1
LOG_LEVEL=INFO
UPLOAD_DIR=./uploads
MAX_VIDEO_SIZE=104857600
```

## Database Setup (Optional)

For production, add PostgreSQL:

```yaml
# In docker-compose.yml
postgres:
  image: postgres:13
  environment:
    POSTGRES_DB: storevision
    POSTGRES_USER: admin
    POSTGRES_PASSWORD: secure_password
  volumes:
    - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

## Security Considerations

1. Use HTTPS in production
2. Set secure CORS origins
3. Implement authentication/authorization
4. Use environment variables for secrets
5. Enable rate limiting
6. Add request validation
7. Use API keys for external access

## Performance Optimization

1. Use CDN for static files
2. Enable caching headers
3. Optimize video processing
4. Use database indexing
5. Monitor resource usage
6. Set up auto-scaling

## Monitoring & Logging

1. Use cloud logging services (CloudWatch, Stackdriver)
2. Set up monitoring alerts
3. Track API metrics
4. Monitor system resources
5. Use error tracking (Sentry)

## Troubleshooting

### Port Already in Use

```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# Linux/Mac
lsof -i :8000
kill -9 <pid>
```

### Out of Memory

- Reduce frame sampling rate
- Enable video compression
- Use GPU acceleration
- Implement batch processing

### Slow Performance

- Profile code with py-spy
- Check CPU/memory usage
- Optimize video codec
- Use caching

## Support

For deployment issues, refer to:
- Documentation: See README.md
- Issues: GitHub Issues
- Discussion: GitHub Discussions
