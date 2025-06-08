#!/bin/bash

# Deploy mcp-sec-10ks to Heroku using Container Registry
# Usage: ./deploy_heroku.sh

set -e

APP_NAME="mcp-sec-10ks"

echo "🚀 Deploying mcp-dolt-database to Heroku..."
echo "App name: $APP_NAME"

# Check if Dockerfile exists
if [ ! -f "Dockerfile" ]; then
    echo "❌ Error: Dockerfile not found in current directory"
    exit 1
fi

# Login to Heroku Container Registry
echo "🔐 Logging into Heroku Container Registry..."
heroku container:login

# Build and push the Docker image
echo "🔨 Building and pushing Docker image..."
heroku container:push web -a "$APP_NAME"

# Release the container
echo "🚢 Releasing the container..."
heroku container:release web -a "$APP_NAME"

echo "✅ mcp-sec-10ks successfully!"
echo "🌐 App URL: https://$APP_NAME.herokuapp.com"

# Optional: Open in browser
read -p "Open app in browser? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    heroku open -a "$APP_NAME"
fi
