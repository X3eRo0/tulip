#!/bin/bash
# Stop packet capture
# Stops the tcpdump process started by start_capture.sh

set -e

# Configuration
PID_FILE="/tmp/tulip_tcpdump.pid"

echo "=== Stopping Packet Capture ==="

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo "Error: This script requires root privileges to stop tcpdump."
    echo "Please run with sudo: sudo ./stop_capture.sh"
    exit 1
fi

# Check if PID file exists
if [ ! -f "$PID_FILE" ]; then
    echo "Warning: PID file not found. tcpdump may not be running."
    echo "Searching for running tcpdump processes..."
    
    # Look for tcpdump processes
    TCPDUMP_PIDS=$(pgrep -f "tcpdump.*capture-.*\.pcap" || true)
    
    if [ -z "$TCPDUMP_PIDS" ]; then
        echo "No tcpdump processes found."
        exit 0
    else
        echo "Found tcpdump processes with PIDs: $TCPDUMP_PIDS"
        read -p "Kill these processes? (y/N): " confirm
        if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
            echo "$TCPDUMP_PIDS" | xargs kill
            echo "✓ tcpdump processes killed"
        fi
        exit 0
    fi
fi

# Read PID from file
TCPDUMP_PID=$(cat "$PID_FILE")

# Check if process is still running
if ! kill -0 "$TCPDUMP_PID" 2>/dev/null; then
    echo "Warning: tcpdump process (PID: $TCPDUMP_PID) is not running."
    rm -f "$PID_FILE"
    exit 0
fi

# Stop tcpdump
echo "Stopping tcpdump process (PID: $TCPDUMP_PID)..."
kill "$TCPDUMP_PID"

# Wait for process to stop
sleep 2

# Check if it stopped
if kill -0 "$TCPDUMP_PID" 2>/dev/null; then
    echo "Process still running, forcing kill..."
    kill -9 "$TCPDUMP_PID"
    sleep 1
fi

# Clean up PID file
rm -f "$PID_FILE"

echo "✓ Packet capture stopped successfully"
echo ""
echo "Capture files are saved in: ./services/test_pcap/"
echo "To start capture again: ./start_capture.sh"
echo ""
echo "Recent capture files:"
ls -la ./services/test_pcap/capture-*.pcap 2>/dev/null | tail -5 || echo "No capture files found"