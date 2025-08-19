#!/bin/bash
# Start Tulip CTF Environment
# Builds and starts all docker services

set -e

echo "=== Starting Tulip CTF Environment ==="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Error: .env file not found!"
    echo "Please run setup_ctf.py first to configure your environment."
    exit 1
fi

# Check if docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running!"
    echo "Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose > /dev/null 2>&1; then
    echo "Error: docker-compose not found!"
    echo "Please install docker-compose and try again."
    exit 1
fi

# Create necessary directories
echo "Creating necessary directories..."
source .env
mkdir -p "${TRAFFIC_DIR_HOST:-./pcaps}"
mkdir -p "./services/test_pcap"

# Start services with build
echo "Building and starting Tulip services..."
docker-compose up --build -d

# Wait a moment for services to start
sleep 5

# Check service status
echo ""
echo "=== Service Status ==="
docker-compose ps

echo ""
echo "=== Tulip Started Successfully! ==="
echo "Frontend should be available at: http://localhost:3000"
echo "API should be available at: http://localhost:8000"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: ./stop_tulip.sh"
echo "To start packet capture: ./start_capture.sh"