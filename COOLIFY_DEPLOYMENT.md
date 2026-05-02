# Coolify Deployment Guide

This guide will help you deploy the Video Clipping Application to Coolify.

## Prerequisites

- A Coolify instance (self-hosted or cloud)
- A Git repository (GitHub, GitLab, Bitbucket, etc.)
- Basic knowledge of Git

## Step-by-Step Deployment

### 1. Prepare Your Code

```bash
# Navigate to the video clipping directory
cd "video clipping"

# Initialize git repository (if not already done)
git init

# Add all files
git add .

# Commit changes
git commit -m "Initial commit: Video clipping application"

# Add remote repository
git remote add origin https://github.com/yourusername/video-clipping.git

# Push to GitHub
git push -u origin main
```

### 2. Create Application in Coolify

1. **Log in to your Coolify dashboard**
2. **Click "Create New Application"**
3. **Select your Git provider** (GitHub, GitLab, etc.)
4. **Choose your repository** (video-clipping)
5. **Select the branch** (main)

### 3. Configure Application Settings

#### Build Configuration
- **Build Type**: Docker
- **Dockerfile Path**: `Dockerfile` (default)
- **Context**: `/` (root directory)

#### Environment Variables
Add these environment variables:
```
PYTHONUNBUFFERED=1
UPLOAD_DIR=/app/uploads
OUTPUT_DIR=/app/output
TEMP_DIR=/app/temp
```

#### Port Configuration
- **Port**: `8000`

#### Resource Allocation
- **Memory**: Minimum 2GB (recommended 4GB)
- **CPU**: Minimum 1 core (recommended 2 cores)

### 4. Configure Volumes (Persistent Storage)

Add these volume mounts:

| Name | Container Path | Type |
|------|----------------|------|
| uploads | /app/uploads | Volume |
| output | /app/output | Volume |
| temp | /app/temp | Volume |

This ensures your uploaded videos and generated clips persist across deployments.

### 5. Configure Domain (Optional)

1. **Click "Domains"** in your application settings
2. **Add your domain** (e.g., `clips.yourdomain.com`)
3. **Configure SSL** (Let's Encrypt is recommended)

### 6. Deploy

1. **Click "Deploy"** in Coolify
2. **Wait for the build to complete** (may take 5-10 minutes)
3. **Check the logs** for any errors

### 7. Access Your Application

Once deployed, access your application at:
- **With domain**: `https://your-domain.com`
- **Without domain**: `https://your-app-id.coolify-instance.com`

## Troubleshooting

### Build Fails

**Issue**: Docker build fails
- **Solution**: Check the build logs in Coolify
- **Common causes**:
  - Insufficient resources during build
  - Network issues downloading dependencies
  - Missing system dependencies

### Application Won't Start

**Issue**: Container starts but crashes
- **Solution**: Check application logs
- **Common causes**:
  - Port conflicts
  - Insufficient memory
  - Missing volume mounts

### Videos Not Uploading

**Issue**: Upload fails or videos disappear
- **Solution**: Check volume mounts are configured correctly
- **Verify**: `/app/uploads` is mounted to a persistent volume

### Slow Performance

**Issue**: Video processing is very slow
- **Solution**: Increase resource allocation
- **Recommended**: 4GB RAM, 2 CPU cores for better performance

### Out of Memory

**Issue**: Container crashes due to OOM
- **Solution**: Increase memory limit
- **Minimum**: 2GB for small videos
- **Recommended**: 4GB+ for large videos

## Monitoring

### Health Checks

The application includes a health check endpoint:
- **URL**: `/health`
- **Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Retries**: 3

Coolify will automatically restart the container if health checks fail.

### Logs

View logs in Coolify:
1. Go to your application
2. Click "Logs"
3. Select the container
4. View real-time logs

## Updates

### Updating the Application

1. **Make changes to your code**
2. **Commit and push to Git**
3. **Coolify will detect the changes**
4. **Click "Deploy"** to trigger a new build

### Rolling Updates

Coolify supports zero-downtime deployments:
- New version is built
- Traffic is gradually shifted
- Old version is removed after successful deployment

## Scaling

### Horizontal Scaling

For high traffic, you can:
1. **Enable multiple replicas** in Coolify
2. **Use a load balancer** (Coolify provides this)
3. **Share storage** using network volumes

### Vertical Scaling

For better performance:
1. **Increase CPU cores**
2. **Add more RAM**
3. **Use faster storage** (SSD recommended)

## Security

### Recommended Security Settings

1. **Enable SSL/TLS** (Let's Encrypt)
2. **Use strong passwords** if you add authentication
3. **Restrict access** by IP if needed
4. **Regular updates** - keep dependencies updated

### Firewall Rules

Ensure these ports are accessible:
- **80/443**: HTTP/HTTPS (for web access)
- **8000**: Application port (internal only)

## Backup

### Automated Backups

Configure backups in Coolify:
1. Go to application settings
2. Enable "Automatic Backups"
3. Set backup schedule (daily recommended)
4. Choose backup retention period

### Manual Backup

```bash
# Backup volumes
docker cp <container-id>:/app/uploads ./backup-uploads
docker cp <container-id>:/app/output ./backup-output
```

## Cost Optimization

### Resource Usage

- **Small deployments**: 1GB RAM, 1 CPU core
- **Medium deployments**: 2GB RAM, 2 CPU cores
- **Large deployments**: 4GB+ RAM, 2+ CPU cores

### Storage

- **Estimate**: 1GB per 10 minutes of HD video
- **Recommendation**: Monitor usage and clean up old files

## Support

If you encounter issues:

1. **Check Coolify logs** first
2. **Review this guide** for common solutions
3. **Check the README.md** for application-specific issues
4. **Open an issue** on GitHub for bugs

## Next Steps

After successful deployment:

1. **Test the application** - upload a small video
2. **Configure monitoring** - set up alerts
3. **Optimize resources** - adjust based on usage
4. **Set up backups** - ensure data safety
5. **Customize** - modify the UI or add features

## Additional Resources

- [Coolify Documentation](https://coolify.io/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)