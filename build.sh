#!/bin/bash

# Exit on error
set -e

# Check Python version
PYTHON_VERSION=$(python3 --version)
echo "Current Python version: $PYTHON_VERSION"

if command -v python3.11 &> /dev/null; then
    echo "Using Python 3.11"
    PYTHON_CMD=python3.11
else
    echo "Python 3.11 not found, attempting to use system Python"
    PYTHON_CMD=python3
fi

# Upgrade pip
$PYTHON_CMD -m pip install --upgrade pip

# Install requirements
$PYTHON_CMD -m pip install -r requirements.txt 