# 🚀 Quick Start Guide

Get your Video Clipping Application running in minutes!

## Option 1: Quick Start (Recommended)

### 1. Run the Setup Script

```bash
cd "video clipping"
./start.sh
```

This will:
- Check if Docker is installed
- Create necessary directories
- Build the Docker image
- Start the application

### 2. Access the Application

Open your browser and go to: **http://localhost:8000**

That's it! You're ready to start clipping videos.

## Option 2: Manual Start

### 1. Install Dependencies

```bash
cd "video clipping"
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python main.py
```

### 3. Access the Application

Open your browser and go to: **http://localhost:8000**

## Option 3: Docker Compose

### 1. Build and Start

```bash
cd "video clipping"
docker-compose up -d
```

### 2. Access the Application

Open your browser and go to: **http://localhost:8000**

### 3. View Logs

```bash
docker-compose logs -f
```

### 4. Stop the Application

```bash
docker-compose down
```

## Testing Your Setup

Run the test script to verify everything is working:

```bash
python test_setup.py
```

## First Steps

Once your application is running:

1. **Upload a Video**
   - Click "Upload Video" tab
   - Drag and drop a video file
   - Wait for upload to complete

2. **Analyze the Video**
   - Go to "Video Library"
   - Click "Analyze" on your video
   - Wait for AI analysis (may take several minutes)

3. **Create Clips**
   - Review recommended clips
   - Click "Create Clip" on recommendations
   - Or create custom clips with specific time ranges

4. **Download Clips**
   - Access clips from the output directory
   - Or download them via the web interface

## Common Issues

### Port Already in Use

If port 8000 is already in use:

```bash
# Find what's using the port
lsof -i :8000

# Or use a different port
python main.py --port 8001
```

### Docker Issues

If Docker commands fail:

```bash
# Check Docker status
docker ps

# Restart Docker
sudo systemctl restart docker
```

### Permission Issues

If you get permission errors:

```bash
# Make script executable
chmod +x start.sh

# Or run with sudo
sudo ./start.sh
```

## Next Steps

- 📖 Read the full [README.md](README.md) for detailed documentation
- 🚀 Deploy to Coolify using [COOLIFY_DEPLOYMENT.md](COOLIFY_DEPLOYMENT.md)
- ✅ Use the [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) for production deployment

## Support

- 🐛 Report issues: GitHub Issues
- 📖 Documentation: README.md
- 💬 Community: [Your community link]

## Happy Clipping! 🎬

---

**Need Help?** Check the troubleshooting section in the README.md or open an issue on GitHub.