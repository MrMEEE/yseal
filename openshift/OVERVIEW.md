# OpenShift S2I Deployment Files

This document provides an overview of the OpenShift S2I deployment configuration created for the ySEal Django project.

## Files Created

### 1. S2I Configuration (`.s2i/` directory)

#### `.s2i/environment`
- Sets environment variables for the S2I build process
- Configures Python and Django settings
- Specifies Gunicorn as the WSGI server

#### `.s2i/bin/assemble` (executable)
- Custom build script that runs during image build
- Installs Python dependencies from `requirements-openshift.txt`
- Collects Django static files
- Prepares the application for deployment

#### `.s2i/bin/run` (executable)
- Custom startup script that runs when container starts
- Executes database migrations automatically
- Starts Gunicorn with proper configuration
- Includes health check endpoints

#### `.s2i/bin/usage` (executable)
- Provides usage information for the S2I image
- Documents environment variables and configuration options

### 2. Application Configuration

#### `gunicorn.conf.py`
- Production-ready Gunicorn configuration
- Configures worker processes based on CPU count
- Sets up logging, timeouts, and performance tuning
- Binds to port 8080 (OpenShift standard)

#### `requirements-openshift.txt`
- Includes base requirements from `requirements.txt`
- Adds production dependencies:
  - `gunicorn` - WSGI HTTP server
  - `whitenoise` - Static file serving
  - `psycopg2-binary` - PostgreSQL adapter
  - `dj-database-url` - Database URL parsing

### 3. OpenShift Resources (`openshift/` directory)

#### `openshift/template.yaml`
Complete OpenShift template with parameters for customization. Includes:

**Infrastructure Components:**
- PostgreSQL database with persistent storage (5Gi)
- Redis cache/broker for Celery (256Mi memory)
- Persistent volume for media files (10Gi)

**Application Components:**
- Django web application (2 replicas, rolling updates)
- Celery worker for background tasks
- Celery beat for scheduled tasks
- Automatic database migrations on startup

**Networking:**
- Services for all components
- Route with TLS edge termination
- Internal service discovery

**Security:**
- Secrets for database, Redis, and Django
- Auto-generated passwords
- Resource limits and requests
- Health checks (liveness and readiness probes)

**Features:**
- S2I build from Git repository
- Automatic rebuilds on Git changes (webhook support)
- Rolling updates with zero downtime
- Horizontal pod autoscaling ready
- Configurable resource limits

#### `openshift/deployment.yaml`
Simplified deployment configuration for quick starts. Includes:
- Pre-configured namespace
- All necessary secrets, services, and deployments
- Ready to deploy with `oc apply -f`
- Uses default values (passwords should be changed)

#### `openshift/deploy.sh` (executable)
Automated deployment script that:
- Checks for required tools (`oc` CLI)
- Verifies OpenShift login
- Creates or uses existing project
- Generates secure random passwords
- Processes and applies the template
- Initiates the build process
- Provides post-deployment instructions

**Usage:**
```bash
./openshift/deploy.sh [project-name] [git-repo] [git-branch]
```

### 4. Documentation

#### `openshift/README.md`
Comprehensive deployment guide covering:
- Three deployment methods (template, direct, quick start)
- Component descriptions and architecture
- Configuration and customization
- Post-deployment tasks (superuser, migrations, etc.)
- Monitoring and troubleshooting
- Scaling and updates
- Database backup/restore procedures
- Security considerations
- Production checklist

#### `openshift/DEVELOPMENT.md`
Local development guide for OpenShift Local (CRC):
- Setup instructions for OpenShift Local
- Development configuration tips
- Resource optimization for local deployment
- Debug mode and live reloading
- Testing and troubleshooting
- Performance tuning

## Deployment Methods

### Method 1: Template (Recommended for Production)
```bash
oc process -f openshift/template.yaml | oc apply -f -
```
- Full control over parameters
- Suitable for CI/CD integration
- Production-ready configuration

### Method 2: Direct Deployment (Quick Testing)
```bash
oc apply -f openshift/deployment.yaml
```
- Fastest deployment
- Uses default values
- Good for testing

### Method 3: Automated Script (Easiest)
```bash
./openshift/deploy.sh
```
- Interactive deployment
- Generates secure passwords
- Provides helpful output

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        OpenShift Cluster                     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │                  Route (TLS)                       │    │
│  │              https://yseal-example.com             │    │
│  └───────────────────────┬────────────────────────────┘    │
│                          │                                  │
│  ┌───────────────────────▼────────────────────────────┐    │
│  │           Service: yseal (port 8080)               │    │
│  └───────────────────────┬────────────────────────────┘    │
│                          │                                  │
│  ┌───────────────────────▼────────────────────────────┐    │
│  │   Deployment: yseal (2 replicas)                   │    │
│  │   - Django Application (Gunicorn)                  │    │
│  │   - Health checks                                  │    │
│  │   - Auto-scaling ready                             │    │
│  └─────┬──────────────────────────────────────────────┘    │
│        │                                                    │
│  ┌─────▼──────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  PostgreSQL    │  │    Redis     │  │ Celery Worker│  │
│  │   (5Gi PVC)    │  │  (Cache +    │  │              │  │
│  │                │  │   Broker)    │  │              │  │
│  └────────────────┘  └──────────────┘  └──────────────┘  │
│                                                             │
│  ┌──────────────┐                                          │
│  │ Celery Beat  │  (Scheduled tasks)                       │
│  └──────────────┘                                          │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐ │
│  │          Media Files PVC (10Gi)                      │ │
│  └──────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Features

### High Availability
- 2 replicas of Django application
- Rolling updates with zero downtime
- Health checks ensure only healthy pods receive traffic
- Persistent storage for database and media

### Security
- TLS termination at the route level
- Secrets for sensitive data (passwords, keys)
- Resource limits prevent resource exhaustion
- Non-root containers (OpenShift security)

### Scalability
- Horizontal scaling: `oc scale deployment/yseal --replicas=N`
- Celery workers can be scaled independently
- PostgreSQL and Redis can be upgraded to HA setups

### Monitoring
- Readiness probes ensure pods are ready before routing traffic
- Liveness probes restart unhealthy pods
- Logs available via `oc logs`
- Integration with OpenShift monitoring

### DevOps
- S2I builds from Git repository
- Webhook support for automatic builds
- Easy rollback to previous versions
- CI/CD pipeline ready

## Environment Variables

The deployment uses the following environment variables:

### Required
- `DJANGO_SECRET_KEY` - Django secret key (auto-generated)
- `DB_PASSWORD` - PostgreSQL password (auto-generated)
- `REDIS_PASSWORD` - Redis password (auto-generated)

### Optional (with defaults)
- `DEBUG` - Debug mode (default: False)
- `USE_POSTGRES` - Use PostgreSQL (default: True)
- `DB_NAME` - Database name (default: yseal)
- `DB_USER` - Database user (default: yseal)
- `DB_HOST` - Database host (auto-configured)
- `DB_PORT` - Database port (default: 5432)
- `ALLOWED_HOSTS` - Allowed hosts (default: *)
- `CELERY_BROKER_URL` - Celery broker (auto-configured)
- `REDIS_URL` - Redis cache (auto-configured)

## Resource Requirements

### Minimum
- **Django App**: 256Mi memory, 200m CPU (per replica)
- **PostgreSQL**: 512Mi memory
- **Redis**: 256Mi memory
- **Celery Worker**: 512Mi memory, 500m CPU
- **Celery Beat**: 256Mi memory, 200m CPU
- **Storage**: 15Gi total (5Gi DB + 10Gi media)

### Recommended Production
- **Django App**: 512Mi-1Gi memory, 500m-1 CPU (per replica)
- **PostgreSQL**: 1-2Gi memory with dedicated storage
- **Redis**: 512Mi-1Gi memory
- Scale to 3-5 Django replicas for high traffic

## Post-Deployment Checklist

1. ✅ Verify all pods are running: `oc get pods`
2. ✅ Check application URL: `oc get route yseal`
3. ✅ Create Django superuser
4. ✅ Access admin dashboard: `https://<route>/admin/`
5. ✅ Test API endpoints: `https://<route>/api/`
6. ✅ Verify Celery workers are processing tasks
7. ✅ Check logs for errors
8. ✅ Configure backup strategy
9. ✅ Set up monitoring alerts
10. ✅ Change default passwords in production

## Troubleshooting Quick Reference

```bash
# View all resources
oc get all

# Check pod status
oc get pods
oc describe pod <pod-name>

# View logs
oc logs -f deployment/yseal
oc logs -f bc/yseal  # Build logs

# Access pod shell
POD=$(oc get pods -l app=yseal -o jsonpath='{.items[0].metadata.name}')
oc rsh $POD

# Run Django commands
oc rsh $POD python manage.py <command>

# Restart deployment
oc rollout restart deployment/yseal

# Check events
oc get events --sort-by='.lastTimestamp'
```

## Maintenance

### Updates
```bash
# Rebuild from latest Git code
oc start-build yseal

# Update environment variable
oc set env deployment/yseal NEW_VAR=value

# Scale application
oc scale deployment/yseal --replicas=3
```

### Backups
```bash
# Backup database
POD=$(oc get pods -l app=yseal-postgresql -o jsonpath='{.items[0].metadata.name}')
oc exec $POD -- pg_dump -U yseal yseal > backup.sql

# Backup media files
oc rsync $POD:/opt/app-root/src/media ./media-backup
```

## Next Steps

1. **Customize for your environment**: Update Git repository URL, domain name, etc.
2. **Configure secrets**: Change default passwords for production
3. **Set up monitoring**: Integrate with Prometheus/Grafana
4. **Configure backups**: Set up automated database backups
5. **CI/CD Pipeline**: Create a CI/CD pipeline for automated deployments
6. **High Availability**: Configure PostgreSQL and Redis HA
7. **Custom Domain**: Configure custom domain and SSL certificate
8. **Performance Testing**: Load test and tune resource limits

## Support

For issues or questions:
- OpenShift Documentation: https://docs.openshift.com/
- ySEal Repository: https://github.com/MrMEEE/yseal
- Django Documentation: https://docs.djangoproject.com/

---

**Created for ySEal - Your Security Enhanced Architecture Library**
