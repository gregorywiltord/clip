#!/bin/bash

# Video Clipping Application - Quick Start Script
# This script helps you get started quickly

set -e

echo "🎬 Video Clipping Application - Quick Start"
echo "============================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✅ Docker is installed"
echo ""

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker Compose is installed"
echo ""

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p uploads output temp
echo "✅ Directories created"
echo ""

# Build and start the application
echo "🔨 Building Docker image..."
docker-compose build
echo "✅ Build completed"
echo ""

echo "🚀 Starting the application..."
docker-compose up -d
echo "✅ Application started"
echo ""

# Wait for the application to be ready
echo "⏳ Waiting for the application to be ready..."
sleep 10

# Check if the application is running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Application is running!"
    echo ""
    echo "🎉 Success! Your Video Clipping Application is now running."
    echo ""
    echo "📍 Access the application at: http://localhost:8000"
    echo ""
    echo "📋 Useful commands:"
    echo "  - View logs: docker-compose logs -f"
    echo "  - Stop application: docker-compose down"
    echo "  - Restart application: docker-compose restart"
    echo "  - Check status: docker-compose ps"
    echo ""
    echo "📖 For more information, see README.md"
    echo "🚀 For Coolify deployment, see COOLIFY_DEPLOYMENT.md"
else
    echo "❌ Application failed to start. Check the logs with: docker-compose logs"
    exit 1
fi