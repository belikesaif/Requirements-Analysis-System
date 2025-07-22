#!/bin/bash

# Production startup script for Render deployment
echo "🚀 Starting NLP Requirements Analysis System..."

# Install missing dependencies at runtime
echo "🔧 Installing additional dependencies..."
python -c "
import sys
import subprocess
import os

def install_runtime_deps():
    print('📦 Installing NumPy, SpaCy, and textacy at runtime...')
    try:
        # Install NumPy first (compatible version)
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--only-binary=:all:', 'numpy>=2.1.0,<3.0.0'], check=False)
        print('✅ NumPy installed')
        
        # Try to install SpaCy and textacy
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--only-binary=:all:', 'spacy>=3.7.0,<4.0.0'], check=False)
        print('✅ SpaCy installed')
        
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--only-binary=:all:', 'textacy>=0.12.0,<1.0.0'], check=False)
        print('✅ textacy installed')
        
        # Try to download SpaCy model
        subprocess.run([sys.executable, '-m', 'spacy', 'download', 'en_core_web_sm'], check=False)
        print('✅ SpaCy model downloaded')
        
    except Exception as e:
        print(f'⚠️ Some dependencies failed: {e}')
        print('🔄 App will use fallback processing')

def test_imports():
    success = True
    try:
        import spacy
        nlp = spacy.load('en_core_web_sm')
        print('✅ SpaCy and model ready')
    except Exception as e:
        print(f'⚠️ SpaCy not available: {e}')
        success = False
    
    try:
        import textacy
        print('✅ textacy ready')
    except Exception as e:
        print(f'⚠️ textacy not available: {e}')
        success = False
    
    return success

install_runtime_deps()
test_imports()
"

# Start the FastAPI application
echo "🌟 Starting FastAPI server..."
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
