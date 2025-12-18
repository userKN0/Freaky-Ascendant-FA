#!/bin/bash
# requirements.sh - Install required Python packages for update_bot.py
# Run this script to install all dependencies on Unix/Linux systems

set -e  # Exit on error

echo "============================================"
echo "Installing Python packages for update_bot.py"
echo "============================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed or not in PATH"
    echo "Please install Python 3.8 or higher before running this script"
    exit 1
fi

# Display Python version
PYTHON_VERSION=$(python3 --version)
echo "Found: $PYTHON_VERSION"
echo ""

# Check if pip3 is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed or not in PATH"
    echo "Please install pip3 before running this script"
    echo "On Ubuntu/Debian: sudo apt install python3-pip"
    echo "On Fedora/RHEL: sudo dnf install python3-pip"
    echo "On macOS: python3 -m ensurepip --upgrade"
    exit 1
fi

echo "Installing packages from requirements.txt..."
echo ""

# Install packages using pip3
python3 -m pip install --user -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "============================================"
    echo "✓ All packages installed successfully!"
    echo "============================================"
    echo ""
    echo "You can now run the bot with:"
    echo "  python3 update_bot.py"
    echo ""
else
    echo ""
    echo "============================================"
    echo "✗ Installation failed!"
    echo "============================================"
    echo ""
    echo "Please check the error messages above and try again"
    exit 1
fi
