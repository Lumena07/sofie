#!/bin/bash

# Exit on error
set -e

# Function to install dependencies for a specific endpoint
install_deps() {
    local endpoint=$1
    local req_file="api/requirements-${endpoint}.txt"
    
    if [ -f "$req_file" ]; then
        echo "Installing dependencies for ${endpoint}..."
        # Use --no-cache-dir to reduce size
        # Use --no-deps to avoid installing unnecessary dependencies
        python3 -m pip install --no-cache-dir --no-deps -r "$req_file"
    fi
}

# Install dependencies for each endpoint
install_deps "query"
install_deps "update"
install_deps "health"

# Clean up unnecessary files
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
find . -type f -name "*.pyd" -delete
find . -type d -name "tests" -exec rm -rf {} +
find . -type d -name "test" -exec rm -rf {} +
find . -type f -name "*.md" -delete
find . -type f -name "*.rst" -delete
find . -type f -name "*.txt" ! -name "requirements*.txt" -delete 