#!/bin/bash

echo "🚀 Deploying NLP Requirements Analysis System"
echo "=============================================="

# Check if git is available
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install Git first."
    exit 1
fi

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Not in a Git repository. Please run this script from the project root."
    exit 1
fi

echo "📝 Committing changes..."
git add .
git commit -m "Deploy: Add deployment configuration and scripts"

echo "📤 Pushing to GitHub..."
git push origin $(git branch --show-current)

echo "✅ Code pushed to GitHub successfully!"
echo ""
echo "Next steps:"
echo "1. Deploy backend to Render:"
echo "   - Go to https://render.com"
echo "   - Create new Web Service"
echo "   - Connect GitHub repo: Requirements-Analysis-System"
echo "   - Set root directory to: backend"
echo "   - Use Python environment"
echo ""
echo "2. Deploy frontend to Vercel:"
echo "   - Run: cd frontend && vercel --prod"
echo "   - Or use Vercel dashboard"
echo ""
echo "📖 See DEPLOYMENT_GUIDE.md for detailed instructions"
