# OpenShift S2I Deployment Guide for ySEal

This directory contains OpenShift deployment configurations for ySEal using Source-to-Image (S2I).

## Prerequisites

- OpenShift cluster (4.x or later)
- `oc` CLI tool installed and configured
- Appropriate permissions to create projects and deployments

## Deployment Options

### Option 1: Using OpenShift Template (Recommended)

The template provides a complete deployment with PostgreSQL, Redis, Celery workers, and the Django application.

```bash
# Create a new project
oc new-project yseal

# Process and apply the template
oc process -f openshift/template.yaml \
  -p APP_NAME=yseal \
  -p GIT_REPOSITORY=https://github.com/MrMEEE/yseal.git \
  -p GIT_BRANCH=main \
  -p PYTHON_VERSION=3.11 \
  | oc apply -f -

# Monitor the build
oc logs -f bc/yseal

# Check deployment status
oc get pods
```

### Option 2: Direct Deployment

For a simpler deployment without template parameters:

```bash
# Apply the deployment configuration
oc apply -f openshift/deployment.yaml

# Start a build
oc start-build yseal

# Monitor the build
oc logs -f bc/yseal
```

### Option 3: Using oc new-app (Quick Start)

```bash
# Create a new project
oc new-project yseal

# Create the application from Git
oc new-app python:3.11~https://github.com/MrMEEE/yseal.git \
  --name=yseal \
  --strategy=source

# Expose the service
oc expose svc/yseal

# Add PostgreSQL
oc new-app postgresql-persistent \
  -p DATABASE_SERVICE_NAME=postgresql \
  -p POSTGRESQL_DATABASE=yseal \
  -p POSTGRESQL_USER=yseal \
  -p POSTGRESQL_PASSWORD=yseal123

# Add Redis
oc new-app redis:6 --name=redis

# Configure environment variables
oc set env deployment/yseal \
  DJANGO_SECRET_KEY=$(openssl rand -base64 50) \
  USE_POSTGRES=True \
  DB_NAME=yseal \
  DB_USER=yseal \
  DB_PASSWORD=yseal123 \
  DB_HOST=postgresql \
  DB_PORT=5432 \
  CELERY_BROKER_URL=redis://redis:6379/0 \
  CELERY_RESULT_BACKEND=redis://redis:6379/0 \
  REDIS_URL=redis://redis:6379/1 \
  ALLOWED_HOSTS='*' \
  DEBUG=False
```

## S2I Configuration

The S2I build process is configured through files in the `.s2i/` directory:

- **`.s2i/environment`** - Environment variables for the build and runtime
- **`.s2i/bin/assemble`** - Custom assemble script that installs dependencies and collects static files
- **`.s2i/bin/run`** - Custom run script that runs migrations and starts Gunicorn

## Components

### Django Application

- **Image**: Python 3.11 S2I builder
- **Replicas**: 2 (for high availability)
- **Port**: 8080
- **Health Checks**: Liveness and readiness probes on `/`
- **Resources**: 
  - Requests: 256Mi memory, 200m CPU
  - Limits: 512Mi memory, 1 CPU

### PostgreSQL Database

- **Image**: Red Hat PostgreSQL 13
- **Storage**: 5Gi persistent volume
- **Resources**: 512Mi memory limit

### Redis Cache

- **Image**: Red Hat Redis 6
- **Resources**: 256Mi memory limit

### Celery Worker

- Processes background tasks
- Resources: 512Mi memory, 500m CPU

### Celery Beat

- Schedules periodic tasks
- Resources: 256Mi memory, 200m CPU

## Configuration

### Environment Variables

The following environment variables are automatically configured:

- `DJANGO_SECRET_KEY` - Auto-generated secure key
- `DEBUG` - Set to `False` in production
- `USE_POSTGRES` - Set to `True`
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` - Database connection
- `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` - Redis connection for Celery
- `REDIS_URL` - Redis connection for caching
- `ALLOWED_HOSTS` - Set to `*` (configure as needed)

### Secrets

Secrets are automatically generated or can be customized:

```bash
# Update Django secret key
oc set data secret/yseal \
  --from-literal=django-secret-key=$(openssl rand -base64 50)

# Update database password
oc set data secret/yseal-postgresql \
  --from-literal=database-password=$(openssl rand -base64 16)

# Update Redis password
oc set data secret/yseal-redis \
  --from-literal=redis-password=$(openssl rand -base64 16)
```

## Post-Deployment Tasks

### Create a Django Superuser

```bash
# Find the yseal pod
POD=$(oc get pods -l app=yseal -o jsonpath='{.items[0].metadata.name}')

# Create superuser interactively
oc rsh $POD python manage.py createsuperuser

# Or use the custom management command
oc rsh $POD python manage.py make_admin <username> <email>
```

### Run Database Migrations

Migrations run automatically on startup, but you can run them manually:

```bash
POD=$(oc get pods -l app=yseal -o jsonpath='{.items[0].metadata.name}')
oc rsh $POD python manage.py migrate
```

### Collect Static Files

Static files are collected during the build process, but you can recollect:

```bash
POD=$(oc get pods -l app=yseal -o jsonpath='{.items[0].metadata.name}')
oc rsh $POD python manage.py collectstatic --noinput
```

### Populate Sample Data

```bash
POD=$(oc get pods -l app=yseal -o jsonpath='{.items[0].metadata.name}')
oc rsh $POD python manage.py populate_sample_data
```

## Monitoring and Troubleshooting

### View Logs

```bash
# Application logs
oc logs -f deployment/yseal

# Celery worker logs
oc logs -f deployment/yseal-celery-worker

# Celery beat logs
oc logs -f deployment/yseal-celery-beat

# PostgreSQL logs
oc logs -f deployment/yseal-postgresql

# Redis logs
oc logs -f deployment/yseal-redis

# Build logs
oc logs -f bc/yseal
```

### Check Pod Status

```bash
oc get pods
oc describe pod <pod-name>
```

### Access the Application

```bash
# Get the route URL
oc get route yseal -o jsonpath='{.spec.host}'

# Or open in browser
xdg-open https://$(oc get route yseal -o jsonpath='{.spec.host}')
```

### Debug Pod Issues

```bash
# Open a shell in the pod
POD=$(oc get pods -l app=yseal -o jsonpath='{.items[0].metadata.name}')
oc rsh $POD

# Run Django shell
oc rsh $POD python manage.py shell

# Check environment variables
oc rsh $POD env | grep -E '(DJANGO|DB_|REDIS|CELERY)'
```

## Scaling

### Scale the Django Application

```bash
# Scale up
oc scale deployment/yseal --replicas=3

# Scale down
oc scale deployment/yseal --replicas=1
```

### Scale Celery Workers

```bash
oc scale deployment/yseal-celery-worker --replicas=3
```

## Updates and Rollbacks

### Trigger a New Build

```bash
# From the latest Git code
oc start-build yseal

# From a specific Git branch/tag
oc start-build yseal --from-ref=feature-branch

# Watch the build
oc logs -f bc/yseal
```

### Rollback a Deployment

```bash
# List deployment history
oc rollout history deployment/yseal

# Rollback to previous version
oc rollout undo deployment/yseal

# Rollback to specific revision
oc rollout undo deployment/yseal --to-revision=2
```

## Storage

### Persistent Volumes

- **PostgreSQL Data**: 5Gi - `/var/lib/pgsql/data`
- **Media Files**: 10Gi - `/opt/app-root/src/media`

### Backup Database

```bash
POD=$(oc get pods -l app=yseal-postgresql -o jsonpath='{.items[0].metadata.name}')
oc exec $POD -- pg_dump -U yseal yseal > yseal-backup-$(date +%Y%m%d).sql
```

### Restore Database

```bash
POD=$(oc get pods -l app=yseal-postgresql -o jsonpath='{.items[0].metadata.name}')
cat yseal-backup.sql | oc exec -i $POD -- psql -U yseal yseal
```

## Security Considerations

1. **Change default passwords** in production (see Secrets section)
2. **Configure ALLOWED_HOSTS** properly for your domain
3. **Enable SSL/TLS** - Routes use edge termination by default
4. **Network Policies** - Consider implementing network policies to restrict pod communication
5. **Resource Quotas** - Set appropriate resource quotas for your namespace
6. **RBAC** - Use proper role-based access control

## Production Checklist

- [ ] Change all default passwords and secrets
- [ ] Configure proper ALLOWED_HOSTS
- [ ] Set appropriate resource limits
- [ ] Enable monitoring and alerts
- [ ] Configure backup strategy
- [ ] Set up log aggregation
- [ ] Configure network policies
- [ ] Review security context constraints
- [ ] Test high availability
- [ ] Configure custom domain and SSL certificate
- [ ] Set up CI/CD pipeline

## Additional Resources

- [OpenShift Documentation](https://docs.openshift.com/)
- [Django on OpenShift](https://www.openshift.com/learn/topics/python)
- [S2I Python Builder](https://github.com/sclorg/s2i-python-container)
- [ySEal Repository](https://github.com/MrMEEE/yseal)
