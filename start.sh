#!/bin/bash
echo "🚀 Starting Intrinsic Value Calculator..."

# Check if frontend is built
if [ -d "project/dist" ]; then
    echo "✅ Frontend build found"
else
    echo "⚠️  Frontend not found - API only mode"
fi

# Start the API server
echo "🚀 Starting API server..."
python api_server.py