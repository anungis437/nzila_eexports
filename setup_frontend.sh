#!/bin/bash

# Create UI component directories
mkdir -p frontend/src/components/ui
mkdir -p frontend/src/pages
mkdir -p frontend/src/hooks

# Install dependencies
echo "Installing frontend dependencies..."
cd frontend && npm install

echo "Frontend setup complete!"
