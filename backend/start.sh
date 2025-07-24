#!/bin/bash

# Production startup script for Render deployment
echo "🚀 Starting NLP Requirements Analysis System..."

# Validate SpaCy installation before starting the app
echo "🔍 Validating SpaCy installation..."
python validate_spacy.py
if [ $? -ne 0 ]; then
    echo "❌ SpaCy validation failed - cannot start application"
    exit 1
fi

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
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--only-binary=:all:', 'numpy>=2.1.0,<3.0.0'], check=True)
        print('✅ NumPy installed')
        
        # Try to install SpaCy and textacy - REQUIRED
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--only-binary=:all:', 'spacy>=3.7.0,<4.0.0'], check=True)
        print('✅ SpaCy installed')
        
        subprocess.run([sys.executable, '-m', 'pip', 'install', '--only-binary=:all:', 'textacy>=0.12.0,<1.0.0'], check=True)
        print('✅ textacy installed')
        
        # Download SpaCy model - REQUIRED
        result = subprocess.run([sys.executable, '-m', 'spacy', 'download', 'en_core_web_sm'], check=False)
        if result.returncode != 0:
            print('⚠️ SpaCy model download failed, trying alternative method...')
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl'], check=True)
        
        # Verify SpaCy model is available
        subprocess.run([sys.executable, '-c', 'import spacy; nlp = spacy.load("en_core_web_sm"); print("SpaCy model verified")'], check=True)
        print('✅ SpaCy model verified and working')
        
    except Exception as e:
        print(f'❌ CRITICAL: SpaCy setup failed: {e}')
        print('� Cannot continue without SpaCy - exiting')
        sys.exit(1)































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