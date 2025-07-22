#!/bin/bash

# Production startup script for Render deployment
echo "🚀 Starting NLP Requirements Analysis System..."

# Install missing dependencies at runtime with enhanced error handling
echo "🔧 Installing additional dependencies..."
python -c "
import sys
import subprocess
import os

def run_command(cmd, description):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode == 0:
            print(f'✅ {description} - SUCCESS')
            return True
        else:
            print(f'⚠️ {description} - WARNING: {result.stderr}')
            return False
    except Exception as e:
        print(f'❌ {description} - ERROR: {e}')
        return False

def install_runtime_deps():
    print('📦 Installing runtime dependencies...')
    
    # Install NumPy first (compatible version)
    run_command([sys.executable, '-m', 'pip', 'install', '--only-binary=:all:', 'numpy>=2.1.0,<3.0.0'], 'NumPy installation')
    
    # Install SpaCy
    run_command([sys.executable, '-m', 'pip', 'install', '--only-binary=:all:', 'spacy>=3.7.0,<4.0.0'], 'SpaCy installation')
    
    # Install textacy
    run_command([sys.executable, '-m', 'pip', 'install', '--only-binary=:all:', 'textacy>=0.12.0,<1.0.0'], 'textacy installation')
    
    # Try multiple methods to download SpaCy model
    print('📥 Attempting to download SpaCy model...')
    
    # Method 1: Direct download
    if run_command([sys.executable, '-m', 'spacy', 'download', 'en_core_web_sm'], 'SpaCy model download (method 1)'):
        return True
    
    # Method 2: Force download with --upgrade
    if run_command([sys.executable, '-m', 'spacy', 'download', 'en_core_web_sm', '--upgrade'], 'SpaCy model download (method 2)'):
        return True
    
    # Method 3: Install via pip
    if run_command([sys.executable, '-m', 'pip', 'install', 'https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl'], 'SpaCy model pip install (method 3)'):
        return True
    
    print('⚠️ All SpaCy model download methods failed - app will use fallbacks')
    return False

def test_imports():
    print('🧪 Testing imports...')
    success_count = 0
    
    # Test NumPy
    try:
        import numpy
        print(f'✅ NumPy {numpy.__version__} ready')
        success_count += 1
    except Exception as e:
        print(f'❌ NumPy failed: {e}')
    
    # Test SpaCy
    try:
        import spacy
        print(f'✅ SpaCy {spacy.__version__} ready')
        success_count += 1
        
        # Test model loading
        try:
            nlp = spacy.load('en_core_web_sm')
            print('✅ SpaCy en_core_web_sm model loaded successfully')
            success_count += 1
        except Exception as e:
            print(f'⚠️ SpaCy model loading failed: {e}')
            print('🔄 App will use basic NLP processing')
            
    except Exception as e:
        print(f'❌ SpaCy failed: {e}')
    
    # Test textacy
    try:
        import textacy
        print(f'✅ textacy {textacy.__version__} ready')
        success_count += 1
    except Exception as e:
        print(f'❌ textacy failed: {e}')
    
    print(f'📊 Dependencies status: {success_count}/4 successful')
    return success_count >= 2  # At least basic functionality

# Execute installation and testing
install_runtime_deps()
if test_imports():
    print('🎉 Runtime dependencies ready!')
else:
    print('⚠️ Some dependencies missing, but app will still start with fallbacks')
"

# Start the FastAPI application
echo "🌟 Starting FastAPI server..."
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
