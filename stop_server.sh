#!/bin/bash
# stop_server.sh - Stop the game server and any processes with "godfinger" in the name
# Exit with 0 on success

echo "Stopping game server process..."

# Stop the main server process (adjust process name as needed)
pkill -f "mbiided.i386" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "Game server stopped successfully."
else
    echo "No game server process found."
fi

echo ""
echo "Stopping Python processes with 'godfinger' in the name..."
pkill -f "python.*godfinger" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "Python godfinger processes stopped successfully."
else
    echo "No Python godfinger processes found."
fi

echo ""
echo "Stopping shell processes with 'godfinger' in the name..."
pkill -f "bash.*godfinger" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "Shell godfinger processes stopped successfully."
else
    echo "No shell godfinger processes found."
fi

exit 0
