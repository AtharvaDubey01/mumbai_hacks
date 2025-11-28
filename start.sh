#!/bin/bash

# Misinformation Detection System - Quick Start Script
# This script helps you get started quickly

echo "🔍 Misinformation Detection System - Quick Start"
echo "=================================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop first."
    echo "   Visit: https://www.docker.com/products/docker-desktop"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed."
    exit 1
fi

echo "✅ Docker is installed"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your NewsAPI key!"
    echo "   Get a free key from: https://newsapi.org/"
    echo ""
    echo "   Open .env with: nano .env"
    echo ""
    read -p "Press Enter when you've added your API key..."
fi

echo ""
echo "🚀 Starting all services with Docker Compose..."
echo ""

# Build and start services
docker-compose up --build

# Note: The script will block here until Ctrl+C
