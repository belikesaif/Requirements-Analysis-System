#!/bin/bash

# Production startup script for Render deployment
echo "🚀 Starting NLP Requirements Analysis System..."

# Install missing dependencies at runtime
echo "🔧 Installing additional dependencies..."
python -c "
import sys
import subprocess

def install_runtime_deps():
    print('📦 Installing NumPy and SpaCy at runtime...')
    try:
        # Install NumPy first (compatible version)
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--only-binary=:all:', 'numpy>=2.1.0,<3.0.0'], check=False)
        print('✅ NumPy installed')
        
        # Try to install SpaCy
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--only-binary=:all:', 'spacy>=3.7.0,<4.0.0'], check=False)
        print('✅ SpaCy installed')
        
        # Try to download model
        subprocess.run([sys.executable, '-m', 'spacy', 'download', 'en_core_web_sm'], check=False)
        print('✅ SpaCy model downloaded')
        
    except Exception as e:
        print(f'⚠️ Some dependencies failed: {e}')
        print('🔄 App will use fallback processing')

def test_imports():
    try:
        import spacy
        nlp = spacy.load('en_core_web_sm')
        print('✅ SpaCy ready')
        return True
    except:
        print('⚠️ SpaCy not available, using fallbacks')
        return False

install_runtime_deps()
test_imports()
"

# Start the FastAPI application
echo "🌟 Starting FastAPI server..."
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
