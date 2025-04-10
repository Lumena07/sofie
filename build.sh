#!/bin/bash

# Exit on error
set -e

# Check Python version
PYTHON_VERSION=$(python3 --version)
echo "Current Python version: $PYTHON_VERSION"

# Upgrade pip
python3 -m pip install --upgrade pip

# Install core dependencies first
python3 -m pip install typing-extensions==4.9.0
python3 -m pip install pydantic==2.5.3
python3 -m pip install starlette==0.32.0.post1
python3 -m pip install fastapi==0.108.0

# Install the rest of the requirements
python3 -m pip install -r requirements.txt 