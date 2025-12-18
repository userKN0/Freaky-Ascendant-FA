#!/bin/bash
# verify_stop.sh - Verify that the game server is NOT running
# Exits with 0 if server is stopped, 1 if still running

# Check if the server process is running (adjust process name as needed)
pgrep -f "mbiided.i386" >/dev/null 2>&1
if [ $? -eq 0 ]; then
    # Process is still running
    exit 1
else
    # Process is stopped
    exit 0
fi
