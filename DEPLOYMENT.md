# Deployment Guide

This guide covers deploying Freshly to various platforms.

## Option 1: Railway (Recommended for Backend)

### Backend Deployment

1. Sign up at [Railway.app](https://railway.app)
2. Create a new project
3. Add PostgreSQL database:
   - Click "New" → "Database" → "PostgreSQL"
   - Note the connection string

4. Deploy backend:
   - Click "New" → "GitHub Repo"
   - Select your repository
   - Set root directory to `/backend`
   - Railway will auto-detect the Dockerfile

5. Set environment variables:
   ```
   DATABASE_URL=<from PostgreSQL service>
   SECRET_KEY=<generate with: openssl rand -hex 32>
   VERYFI_API_KEY=<your-veryfi-key>
   OPENAI_API_KEY=<your-openai-key>
   CORS_ORIGINS=["https://your-frontend.vercel.app"]
   ```

6. The app will automatically build and deploy

## Option 2: Render

### Backend Deployment

1. Sign up at [Render.com](https://render.com)
2. Create a new Web Service
3. Connect your GitHub repository
4. Configure:
   - Name: freshly-api
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

5. Create PostgreSQL database:
   - Dashboard → New → PostgreSQL
   - Name: freshly-db

6. Link database to web service:
   - Add environment variable: `DATABASE_URL` from database

7. Add other environment variables (same as Railway)

## Frontend Deployment (Vercel)

1. Sign up at [Vercel.com](https://vercel.com)
2. Import your repository
3. Configure:
   - Framework Preset: Vite
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`

4. Set environment variable:
   ```
   VITE_API_URL=https://your-backend-url.railway.app
   ```

5. Deploy

## Local Development with Docker

```bash
# Start all services
docker-compose up

# Backend will be at http://localhost:8000
# Frontend will be at http://localhost:5173
# PostgreSQL at localhost:5432
# Redis at localhost:6379

# Stop services
docker-compose down

# Reset database
docker-compose down -v
```

## Environment Variables Reference

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# API Keys
VERYFI_API_KEY=your-veryfi-api-key
VERYFI_CLIENT_ID=your-veryfi-client-id
VERYFI_USERNAME=your-veryfi-username
OPENAI_API_KEY=your-openai-api-key

# Application
DEBUG=False
CORS_ORIGINS=["https://your-frontend-domain.com"]

# Upload Settings
MAX_UPLOAD_SIZE=10485760
UPLOAD_DIR=./uploads
RECEIPTS_DIR=./receipts

# Redis
REDIS_URL=redis://localhost:6379/0
```

### Frontend (.env)

```bash
VITE_API_URL=https://your-backend-url.com
VITE_APP_NAME=Freshly
```

## Post-Deployment Checklist

- [ ] Run database migrations: `alembic upgrade head`
- [ ] Test user registration and login
- [ ] Verify API endpoints are accessible
- [ ] Test receipt upload (ensure OCR API key is valid)
- [ ] Test AI meal suggestions (ensure OpenAI API key is valid)
- [ ] Check CORS settings allow frontend domain
- [ ] Verify file uploads work correctly
- [ ] Test PWA installation on mobile
- [ ] Monitor logs for errors
- [ ] Set up monitoring/alerting (optional)

## Troubleshooting

### Backend Issues

**Database connection failed:**
- Verify DATABASE_URL is correct
- Check if PostgreSQL service is running
- Ensure firewall allows connections

**CORS errors:**
- Add frontend URL to CORS_ORIGINS in backend .env
- Restart backend service

**Receipt processing fails:**
- Verify OCR API key is valid
- Check API quota/limits
- Review logs for specific error

### Frontend Issues

**API calls fail:**
- Verify VITE_API_URL points to backend
- Check backend CORS settings
- Ensure backend is running

**Build fails:**
- Clear node_modules: `rm -rf node_modules && npm install`
- Check Node version (requires 18+)

## Monitoring

### Recommended Tools

- **Sentry** - Error tracking
- **LogRocket** - Session replay
- **Uptime Robot** - Uptime monitoring
- **PostHog** - Product analytics

## Scaling Considerations

As your app grows:

1. **Database**: Upgrade to managed PostgreSQL (AWS RDS, Render Pro, etc.)
2. **File Storage**: Move to S3/CloudFlare R2 for receipts
3. **Caching**: Use Redis for caching frequently accessed data
4. **Background Jobs**: Use Celery for OCR processing
5. **CDN**: Use CloudFlare for static assets

## Security Checklist

- [ ] Use strong SECRET_KEY (32+ random characters)
- [ ] Enable HTTPS only
- [ ] Set secure CORS origins (no wildcards in production)
- [ ] Rate limit API endpoints
- [ ] Validate file uploads (size, type)
- [ ] Sanitize user inputs
- [ ] Regular dependency updates
- [ ] Enable database backups
- [ ] Use environment variables (never commit secrets)

## Cost Estimates

### Free Tier (Good for starting):
- **Railway**: Free $5/month credits
- **Render**: Free tier for web services
- **Vercel**: Free for personal projects
- **PostgreSQL**: Free tier on Render/Railway
- **Veryfi**: 200 free receipts/month
- **OpenAI**: Pay per use (~$0.002 per request)

**Total**: $0-5/month for light usage

### Production (1000 users):
- **Backend Hosting**: $20-50/month
- **Database**: $20-40/month
- **File Storage**: $5-10/month
- **OCR API**: $20-50/month (based on usage)
- **OpenAI API**: $10-30/month

**Total**: $75-180/month

## Support

For deployment issues:
1. Check logs in your hosting dashboard
2. Review this guide's troubleshooting section
3. Open an issue on GitHub
4. Contact platform support (Railway, Render, Vercel)
