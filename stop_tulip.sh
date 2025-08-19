#!/bin/bash
# Stop Tulip CTF Environment
# Stops all docker services

set -e

echo "=== Stopping Tulip CTF Environment ==="

# Check if docker-compose is available
if ! command -v docker-compose > /dev/null 2>&1; then
    echo "Error: docker-compose not found!"
    exit 1
fi

# Stop services
echo "Stopping Tulip services..."
docker-compose down

# Show final status
echo ""
echo "=== Final Status ==="
docker-compose ps

echo ""
echo "=== Tulip Stopped Successfully! ==="
echo ""
echo "To start again: ./start_tulip.sh"
echo "To stop packet capture: ./stop_capture.sh"
echo ""
echo "Note: To completely remove containers and volumes, run:"
echo "  docker-compose down -v --remove-orphans"