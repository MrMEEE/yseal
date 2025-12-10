# Development Deployment with OpenShift Local

This guide helps you deploy ySEal on OpenShift Local (formerly CodeReady Containers) for local development.

## Prerequisites

1. **Install OpenShift Local**:
   ```bash
   # Download from: https://developers.redhat.com/products/openshift-local/overview
   # Or on Fedora/RHEL:
   sudo dnf install crc
   ```

2. **Setup OpenShift Local**:
   ```bash
   # Setup (requires pull secret from Red Hat)
   crc setup
   
   # Start the cluster
   crc start
   
   # Login to the cluster
   eval $(crc oc-env)
   oc login -u developer https://api.crc.testing:6443
   ```

## Quick Deployment

### Using the deployment script:

```bash
cd openshift
./deploy.sh yseal-dev
```

### Manual deployment:

```bash
# Login to OpenShift Local
eval $(crc oc-env)
oc login -u developer -p developer https://api.crc.testing:6443

# Create project
oc new-project yseal-dev

# Deploy
oc apply -f openshift/deployment.yaml

# Start build
oc start-build yseal

# Wait for build to complete
oc logs -f bc/yseal

# Get the URL
echo "Application URL: http://$(oc get route yseal -o jsonpath='{.spec.host}')"
```

## Development Configuration

For local development, you may want to use smaller resource limits:

```bash
# Scale down replicas
oc scale deployment/yseal --replicas=1

# Reduce resource limits
oc set resources deployment/yseal \
  --limits=cpu=500m,memory=256Mi \
  --requests=cpu=100m,memory=128Mi
```

## Enable Debug Mode

**Warning: Only for development, never in production!**

```bash
oc set env deployment/yseal DEBUG=True
```

## Port Forwarding for Local Development

If you want to access services directly without the route:

```bash
# Forward Django application
oc port-forward deployment/yseal 8080:8080

# Forward PostgreSQL
oc port-forward deployment/yseal-postgresql 5432:5432

# Forward Redis
oc port-forward deployment/yseal-redis 6379:6379
```

## Using SQLite Instead of PostgreSQL

For a lighter development setup:

```bash
# Don't deploy PostgreSQL
# Update the deployment
oc set env deployment/yseal USE_POSTGRES=False

# Remove PostgreSQL resources (optional)
oc delete deployment/yseal-postgresql
oc delete service/yseal-postgresql
oc delete pvc/yseal-postgresql
```

## Live Reloading

For rapid development, you can mount your local code:

```bash
# Create a PVC for code
oc create -f - <<EOF
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: yseal-code
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
EOF

# Copy your code to the PVC
POD=$(oc get pods -l app=yseal -o jsonpath='{.items[0].metadata.name}')
oc rsync . $POD:/opt/app-root/src/ --exclude='.git' --exclude='*.pyc'

# Run with auto-reload (not recommended for production)
oc set env deployment/yseal DJANGO_DEBUG=True
```

## Testing the Deployment

```bash
# Get the route
ROUTE=$(oc get route yseal -o jsonpath='{.spec.host}')

# Test the application
curl http://$ROUTE/

# Test the API
curl http://$ROUTE/api/v1/

# Test admin dashboard
curl http://$ROUTE/dashboard/
```

## Viewing Logs

```bash
# Application logs
oc logs -f deployment/yseal

# All logs from a specific pod
POD=$(oc get pods -l app=yseal -o jsonpath='{.items[0].metadata.name}')
oc logs -f $POD

# PostgreSQL logs
oc logs -f deployment/yseal-postgresql

# Build logs
oc logs -f bc/yseal
```

## Database Management

### Create Superuser

```bash
POD=$(oc get pods -l app=yseal -o jsonpath='{.items[0].metadata.name}')
oc rsh $POD python manage.py createsuperuser
```

### Reset Database

```bash
# Delete and recreate PostgreSQL
oc delete deployment/yseal-postgresql
oc delete pvc/yseal-postgresql

# Redeploy
oc apply -f openshift/deployment.yaml

# Wait for PostgreSQL to be ready
sleep 30

# Run migrations
POD=$(oc get pods -l app=yseal -o jsonpath='{.items[0].metadata.name}')
oc rsh $POD python manage.py migrate
```

### Access PostgreSQL Directly

```bash
POD=$(oc get pods -l app=yseal-postgresql -o jsonpath='{.items[0].metadata.name}')
oc rsh $POD psql -U yseal yseal
```

## Cleanup

```bash
# Delete the project and all resources
oc delete project yseal-dev

# Or delete specific resources
oc delete all -l app=yseal
oc delete pvc -l app=yseal
oc delete secret -l app=yseal
```

## Troubleshooting

### Build Fails

```bash
# Check build logs
oc logs -f bc/yseal

# Rebuild from scratch
oc delete bc/yseal
oc delete is/yseal
oc apply -f openshift/deployment.yaml
oc start-build yseal
```

### Pod Crashes

```bash
# Check pod status
oc get pods
oc describe pod <pod-name>

# Check logs
oc logs <pod-name>

# Get events
oc get events --sort-by='.lastTimestamp'
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
oc get pods -l app=yseal-postgresql

# Test connection
POD=$(oc get pods -l app=yseal -o jsonpath='{.items[0].metadata.name}')
oc rsh $POD env | grep DB_

# Test from Django
oc rsh $POD python manage.py dbshell
```

### Permission Issues

```bash
# OpenShift Local uses restricted security contexts
# If you have permission issues, check:
oc describe pod <pod-name>

# Check security context constraints
oc get scc
```

## Performance Tuning for OpenShift Local

OpenShift Local has limited resources. Adjust as needed:

```bash
# Stop CRC
crc stop

# Configure resources
crc config set cpus 4
crc config set memory 8192

# Start again
crc start
```

## Using with VS Code

You can develop with VS Code and OpenShift:

1. Install the OpenShift Toolkit extension
2. Connect to your OpenShift Local cluster
3. Use the integrated terminal for `oc` commands

## Tips

- **Save Resources**: Only run what you need. Consider disabling Celery workers for simple development
- **Use Image Caching**: Builds will be faster after the first one
- **Watch Resources**: `watch oc get pods` to monitor status
- **Quick Rebuild**: After code changes: `oc start-build yseal --follow`

## Additional Resources

- [OpenShift Local Documentation](https://access.redhat.com/documentation/en-us/red_hat_openshift_local/)
- [OpenShift Developer Guide](https://docs.openshift.com/container-platform/latest/applications/developing-applications.html)
- [Python on OpenShift](https://www.openshift.com/learn/topics/python)
