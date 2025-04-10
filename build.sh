#!/bin/bash

# Exit on error
set -e

# Check Python version
PYTHON_VERSION=$(python3 --version)
echo "Current Python version: $PYTHON_VERSION"

# Upgrade pip without cache
python3 -m pip install --no-cache-dir --upgrade pip

# Install core dependencies first without cache
python3 -m pip install --no-cache-dir typing-extensions==4.9.0
python3 -m pip install --no-cache-dir pydantic==2.5.3
python3 -m pip install --no-cache-dir starlette==0.32.0.post1
python3 -m pip install --no-cache-dir fastapi==0.108.0

# Install the rest of the requirements without cache
python3 -m pip install --no-cache-dir -r requirements.txt 