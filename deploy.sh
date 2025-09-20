#!/bin/bash
# Deployment preparation script

echo "🚀 Preparing Intrinsic Value Calculator for deployment..."

# Build frontend
echo "📦 Building frontend..."
cd project
npm install
npm run build
cd ..

echo "✅ Build complete!"
echo ""
echo "🌐 Your application is ready for deployment!"
echo ""
echo "📋 Deployment Options:"
echo "  1. Railway: Connect your GitHub repo to Railway"
echo "  2. Heroku: heroku create && git push heroku main"
echo "  3. Any Platform: python api_server.py"
echo ""
echo "🔗 Local Production Test: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "Happy deploying! 🎉"