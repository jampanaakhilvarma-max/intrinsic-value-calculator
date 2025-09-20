#!/bin/bash
echo "🚀 Starting Intrinsic Value Calculator..."

# Check if we're in a deployment environment
if [ -n "$RAILWAY_ENVIRONMENT" ] || [ -n "$PORT" ]; then
    echo "📦 Railway deployment detected - building frontend..."
    
    # Only build frontend in deployment, not locally
    if [ -d "project" ] && [ ! -d "project/dist" ]; then
        echo "🔨 Building React frontend for deployment..."
        cd project
        npm install --production
        npm run build
        cd ..
        echo "✅ Frontend build completed"
    else
        echo "✅ Frontend already built or not needed"
    fi
fi

# Start the API server (unchanged)
echo "🚀 Starting API server..."
python api_server.py