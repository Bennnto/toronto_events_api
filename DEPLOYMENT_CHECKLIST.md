# Public API Deployment Checklist

## 1. Security Configuration ⚠️

### Environment & Secrets
- [x] Create `.env.production` file with production environment variables
- [x] Set `SECRET_KEY` to a strong, unique value (min 50 characters)
- [x] Set `DEBUG = False` in production settings
- [x] Ensure `SECRET_KEY` is NOT committed to version control
- [x] Use environment variables for all sensitive data

### ALLOWED_HOSTS & CORS
- [ ] Configure `ALLOWED_HOSTS` with your domain(s)
  ```python
  ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com', 'api.your-domain.com']
  ```
- [x] Configure `CORS_ALLOWED_ORIGINS` for frontend domains
- [x] Disable `CORS_ALLOW_ALL_ORIGINS` (currently may be enabled)
- [x] Add whitelist of allowed origins instead

### HTTPS & SSL
- [x] Enable HTTPS only (set `SECURE_SSL_REDIRECT = True`)
- [x] Set `SESSION_COOKIE_SECURE = True`
- [s] Set `CSRF_COOKIE_SECURE = True`
- [x] Set `SECURE_BROWSER_XSS_FILTER = True`
- [x] Set Content-Security-Policy headers via Django middleware or your reverse proxy
- [ ] Set `X_FRAME_OPTIONS = 'DENY'`
- [ ] Obtain SSL certificate (Let's Encrypt recommended)

### Authentication & Authorization
- [x] Review JWT token expiration times in settings
- [x] Configure `SIMPLE_JWT` settings:
  ```python
  'ACCESS_TOKEN_LIFETIME': timedelta(hours=1)
  'REFRESH_TOKEN_LIFETIME': timedelta(days=7)
  ```
- [x] Implement rate limiting for token endpoints
- [x] Add API key management if needed for third-party clients
- [x] Document JWT auth requirements in API docs: how to send the `Authorization: Bearer <token>` header, how to obtain/refresh tokens, and which endpoints are public vs protected

## 2. Database Migration & Setup 🗄️

### Database Configuration
- [ ] Migrate from SQLite to production database (PostgreSQL recommended)
  ```python
  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.postgresql',
          'NAME': os.getenv('DB_NAME'),
          'USER': os.getenv('DB_USER'),
          'PASSWORD': os.getenv('DB_PASSWORD'),
          'HOST': os.getenv('DB_HOST'),
          'PORT': os.getenv('DB_PORT', '5432'),
      }
  }
  ```
- [ ] Run all migrations: `python manage.py migrate`
- [ ] Create superuser for admin panel
- [ ] Set up database backups schedule
- [ ] Test database connection in staging environment

### Database Performance
- [ ] Add database indexes on frequently filtered fields
- [ ] Configure connection pooling
- [ ] Set up read replicas if needed for scaling

## 3. API Documentation & Versioning 📚

### OpenAPI/Swagger Documentation
- [ ] Verify drf-spectacular is properly configured
- [ ] Generate OpenAPI schema: `python manage.py spectacular --file schema.yml`
- [ ] Test API documentation at `/api/schema/swagger-ui/`
- [ ] Document all endpoints with descriptions
- [ ] Add request/response examples
- [ ] Document error codes and responses
- [ ] Document authentication requirements

### Versioning
- [ ] Confirm versioning scheme (currently `URLPathVersioning` v1)
- [ ] Plan versioning strategy for future changes
- [ ] Document breaking changes process

## 4. Testing & Validation ✅

### Unit & Integration Tests
- [ ] Write tests for all API endpoints
- [ ] Test authentication and authorization
- [ ] Test pagination and filtering
- [ ] Test error handling
- [ ] Achieve minimum 80% code coverage
- [ ] Run: `python manage.py test`

### API Testing
- [ ] Test all CRUD operations
- [ ] Test filters and search functionality
- [ ] Test pagination limits
- [ ] Test rate limiting
- [ ] Test CORS headers with Postman/Insomnia
- [ ] Verify response times under load

### Security Testing
- [ ] SQL injection tests
- [ ] XSS vulnerability tests
- [ ] CSRF token validation
- [ ] Rate limiting verification
- [ ] Test with invalid/expired JWT tokens

## 5. Performance & Caching 🚀

### Caching Strategy
- [ ] Configure Redis or Memcached for caching
  ```python
  CACHES = {
      'default': {
          'BACKEND': 'django_redis.cache.RedisCache',
          'LOCATION': 'redis://127.0.0.1:6379/1',
      }
  }
  ```
- [ ] Implement caching for frequently accessed endpoints
- [ ] Set cache TTL appropriately
- [ ] Test cache invalidation

### Database Query Optimization
- [ ] Use `select_related()` for foreign keys (Category, Venue)
- [ ] Use `prefetch_related()` for reverse relationships
- [ ] Review N+1 query problems
- [ ] Add database query monitoring

### Response Optimization
- [ ] Enable GZIP compression
  ```python
  MIDDLEWARE += ['django.middleware.gzip.GZipMiddleware']
  ```
- [ ] Minimize serializer output fields
- [ ] Implement response filtering by fields

## 6. Logging & Monitoring 📊

### Logging Configuration
- [ ] Set up structured logging (Python logging)
- [ ] Configure log levels for production (WARNING or higher)
- [ ] Log all errors and exceptions
- [ ] Set up log rotation
- [ ] Avoid logging sensitive data (passwords, tokens, PII)

### Monitoring Tools
- [ ] Set up error tracking (Sentry, Rollbar, etc.)
- [ ] Set up performance monitoring (New Relic, DataDog, etc.)
- [ ] Set up uptime monitoring
- [ ] Configure alerts for critical errors
- [ ] Monitor database performance
- [ ] Set up metrics collection

### Audit Trail
- [ ] Log all write operations (POST, PUT, DELETE)
- [ ] Track user actions for compliance
- [ ] Store request/response metadata for debugging

## 7. Rate Limiting & Throttling 🛡️

- [ ] Configure DRF throttling classes
  ```python
  'DEFAULT_THROTTLE_CLASSES': [
      'rest_framework.throttling.AnonRateThrottle',
      'rest_framework.throttling.UserRateThrottle'
  ],
  'DEFAULT_THROTTLE_RATES': {
      'anon': '100/hour',
      'user': '1000/hour'
  }
  ```
- [ ] Implement endpoint-specific rate limits
- [ ] Test rate limit responses
- [ ] Document rate limits in API docs
- [ ] Consider DDoS protection (Cloudflare, etc.)

## 8. Static Files & Media 📁

### Static Files
- [x] Configure `STATIC_ROOT` for production
- [x] Configure `STATIC_URL` appropriately
- [ ] Run `python manage.py collectstatic --noinput`
- [ ] Serve static files via CDN or web server

### Media Files
- [ ] Configure `MEDIA_ROOT` and `MEDIA_URL`
- [ ] Use cloud storage (AWS S3, etc.) if needed
- [ ] Set up file upload validation

## 9. Deployment Infrastructure 🚀

### Server Setup
- [ ] Choose hosting provider (AWS, DigitalOcean, Heroku, etc.)
- [ ] Set up Linux server (Ubuntu 22.04 LTS recommended)
- [ ] Install Python 3.10+ and pip
- [ ] Create isolated Python virtual environment

### Application Server
- [ ] Use production WSGI server (Gunicorn/uWSGI, NOT Django development server)
  ```bash
  gunicorn events.wsgi:application --bind 0.0.0.0:8000 --workers 4
  ```
- [ ] Configure worker processes (4-8 workers recommended)
- [ ] Set up process management (Supervisor, systemd, etc.)

### Web Server
- [ ] Set up Nginx or Apache as reverse proxy
- [ ] Configure Nginx to handle SSL/TLS
- [ ] Configure Nginx to forward requests to Gunicorn
- [ ] Enable Nginx gzip compression
- [ ] Set up security headers (X-Frame-Options, etc.)

### Process Management
- [ ] Set up systemd service for Gunicorn
- [ ] Configure auto-restart on server reboot
- [ ] Set up log rotation for application logs

## 10. CI/CD Pipeline 🔄

- [ ] Set up GitHub Actions (or similar CI/CD tool)
- [ ] Automated testing on every push
- [ ] Code quality checks (flake8, black, isort)
- [ ] Automated deployments to staging
- [ ] Manual approval for production deployments
- [ ] Automated database migrations
- [ ] Health checks after deployment

## 11. Documentation & APIs 📖

### API Documentation
- [ ] Complete README with setup instructions
- [ ] API endpoint documentation
- [ ] Authentication guide
- [ ] Rate limiting documentation
- [ ] Error code reference
- [ ] SDK/client examples (Python, JavaScript, etc.)
- [ ] Postman/Insomnia collection

### Operational Documentation
- [ ] Deployment guide
- [ ] Troubleshooting guide
- [ ] Database backup/restore procedures
- [ ] Scaling procedures
- [ ] Rollback procedures

## 12. Backup & Disaster Recovery 💾

- [ ] Set up automated database backups
- [ ] Test backup restoration process
- [ ] Store backups in multiple locations
- [ ] Document recovery procedures
- [ ] Set backup retention policy
- [ ] Monitor backup job success

## 13. GDPR & Compliance 📋

- [ ] Review data collection and usage
- [ ] Implement data retention policies
- [ ] Add terms of service
- [ ] Add privacy policy
- [ ] Implement right to deletion (if required)
- [ ] Audit logging for compliance

## 14. Health Checks & Status Page 🏥

- [x] Create health check endpoint
  ```python
  @api_view(['GET'])
  def health_check(request):
      return Response({'status': 'healthy'}, status=200)
  ```
- [ ] Monitor health check endpoint
- [ ] Set up status page (Statuspage.io or similar)
- [ ] Include database connectivity check
- [ ] Include external service checks

## 15. Post-Deployment 🎉

- [ ] Verify all endpoints are working in production
- [ ] Test authentication with production credentials
- [ ] Monitor error logs for issues
- [ ] Verify SSL certificate is valid
- [ ] Check API response times
- [ ] Test CORS with actual frontend domain
- [ ] Verify rate limiting is working
- [ ] Monitor resource usage (CPU, memory, disk)
- [ ] Check backup jobs are running

## 16. Maintenance Schedule 🔧

- [ ] Weekly: Monitor error logs, performance metrics
- [ ] Monthly: Review security updates, patch dependencies
- [ ] Quarterly: Security audit, performance review
- [ ] Yearly: Complete infrastructure review, scaling assessment

---

## Quick Start Commands

```bash
# Create production environment
python -m venv venv_prod
source venv_prod/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# Prepare for deployment
python manage.py collectstatic --noinput
python manage.py migrate --settings=events.settings_production

# Run production server
gunicorn events.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

---

**Last Updated:** May 4, 2026  
**Status:** Ready for deployment review
