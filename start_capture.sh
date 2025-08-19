#!/bin/bash

set -e

INTERFACE="wg-ctf"
CAPTURE_DIR="./pcaps"
PID_FILE="/tmp/tulip_tcpdump.pid"

echo "=== Starting Packet Capture ==="
if [ "$EUID" -ne 0 ]; then
    echo "[-] Error: This script requires root privileges for tcpdump."
    echo "[-] Please run with sudo: sudo ./start_capture.sh"
    exit 1
fi

if ! command -v tcpdump >/dev/null 2>&1; then
    echo "Error: tcpdump not found!"
    echo "Please install tcpdump: sudo apt-get install tcpdump"
    exit 1
fi

if ! ip link show "$INTERFACE" >/dev/null 2>&1; then
    echo "[-] Warning: Interface $INTERFACE not found!"
    echo "[-] Available interfaces:"
    ip link show | grep -E "^[0-9]+:" | cut -d: -f2 | tr -d ' '
    echo ""
    read -p "Enter the correct interface name (or press Enter to use $INTERFACE anyway): " input_interface
    if [ -n "$input_interface" ]; then
        INTERFACE="$input_interface"
    fi
fi

if [ -f "$PID_FILE" ]; then
    old_pid=$(cat "$PID_FILE")
    if kill -0 "$old_pid" 2>/dev/null; then
        echo "[-] Error: tcpdump is already running (PID: $old_pid)"
        echo "[-] Stop it first with: ./stop_capture.sh"
        exit 1
    else
        rm -f "$PID_FILE"
    fi
fi

mkdir -p "$CAPTURE_DIR"

echo "[+] Starting tcpdump on interface: $INTERFACE"
echo "[+] Capture directory: $CAPTURE_DIR"
echo "[+] Files will rotate every tick"

nohup tcpdump -i "$INTERFACE" -w "$CAPTURE_DIR/capture-%Y%m%d-%H%M%S.pcap" -G 3600 >/tmp/tulip_tcpdump.log 2>&1 &
TCPDUMP_PID=$!

echo "$TCPDUMP_PID" >"$PID_FILE"
sleep 2
if kill -0 "$TCPDUMP_PID" 2>/dev/null; then
    echo "[+] Packet capture started successfully (PID: $TCPDUMP_PID)"
    echo "[+] Log file: /tmp/tulip_tcpdump.log"
    echo "[+] Capture files: $CAPTURE_DIR/capture-*.pcap"
    echo ""
    echo "To stop capture: ./stop_capture.sh"
    echo "To view log: tail -f /tmp/tulip_tcpdump.log"
else
    echo "[-] Error: tcpdump failed to start!"
    echo "[-] Check log: cat /tmp/tulip_tcpdump.log"
    rm -f "$PID_FILE"
    exit 1
fi
