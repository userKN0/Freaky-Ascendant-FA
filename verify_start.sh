#!/bin/bash
# verify_start.sh - Verify that the game server IS running
# Exits with 0 if server is running, 1 if not running

# Check if the server process is running (adjust process name as needed)
pgrep -f "mbiided.i386" >/dev/null 2>&1
if [ $? -eq 0 ]; then
    # Process is running
    exit 0
else
    # Process is not running
    exit 1
fi
