#!/bin/bash

# Deploy Backend with CORS Fixes to Render
echo "🚀 Deploying Backend with CORS Fixes"
echo "======================================"

# Check if we're in the backend directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Please run this script from the backend directory"
    exit 1
fi

echo "📋 CORS Configuration Summary:"
echo "- Frontend URL: https://nrasfrontend.vercel.app"
echo "- Backend URL: https://requirements-analysis-system.onrender.com"
echo "- CORS: Configured for Vercel deployment"

# Test local backend first (if running)
echo ""
echo "🧪 Testing local CORS configuration..."
if python test_cors.py; then
    echo "✅ Local CORS test passed"
else
    echo "⚠️ Local CORS test failed or backend not running locally"
fi

# Check git status
echo ""
echo "📝 Git Status:"
git status --short

# Add and commit changes
echo ""
echo "💾 Committing CORS fixes..."
git add main.py render.yaml test_cors.py
git commit -m "🔧 Fix CORS configuration for Vercel frontend

- Add specific Vercel URL to allowed origins
- Set FRONTEND_URL environment variable
- Add explicit CORS preflight handler
- Include health check endpoints
- Add CORS testing script

Fixes: Access-Control-Al low-Origin header missing"

# Push to trigger Render deployment
echo ""
echo "🚀 Pushing to trigger Render deployment..."
git push origin $(git branch --show-current)

echo ""
echo "✅ Deployment triggered!"
echo ""
echo "📋 Next Steps:"
echo "1. Wait for Render deployment to complete (3-5 minutes)"
echo "2. Test the API endpoint: https://requirements-analysis-system.onrender.com/health"
echo "3. Test CORS with: python test_cors.py"
echo "4. Verify frontend can connect to backend"
echo ""
echo "🔗 Monitor deployment at:"
echo "   https://dashboard.render.com/"
echo ""
echo "🐛 If issues persist:"
echo "   1. Check Render logs for deployment errors"
echo "   2. Verify environment variables are set correctly"
echo "   3. Test with curl:"
echo "      curl -X OPTIONS https://requirements-analysis-system.onrender.com/api/process-requirements \\"
echo "           -H 'Origin: https://nrasfrontend.vercel.app' \\"
echo "           -H 'Access-Control-Request-Method: POST' \\"
echo "           -v"
