#!/bin/bash

# Production startup script for Render deployment
echo "🚀 Starting NLP Requirements Analysis System..."

# Try to install SpaCy at runtime if not available
echo "🔧 Checking SpaCy installation..."
python -c "
import sys
import subprocess

def install_spacy_runtime():
    try:
        import spacy
        nlp = spacy.load('en_core_web_sm')
        print('✅ SpaCy and model already available')
        return True
    except ImportError:
        print('📦 Installing SpaCy at runtime...')
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', '--only-binary=:all:', 'spacy==3.7.2'], check=True)
            subprocess.run([sys.executable, '-m', 'spacy', 'download', 'en_core_web_sm'], check=True)
            print('✅ SpaCy installed successfully at runtime')
            return True
        except Exception as e:
            print(f'⚠️ SpaCy runtime installation failed: {e}')
            print('🔄 Application will use fallback processing')
            return False
    except OSError:
        print('📥 Downloading SpaCy model...')
        try:
            subprocess.run([sys.executable, '-m', 'spacy', 'download', 'en_core_web_sm'], check=True)
            print('✅ SpaCy model downloaded successfully')
            return True
        except Exception as e:
            print(f'⚠️ Model download failed: {e}')
            print('🔄 Application will use fallback processing')
            return False

install_spacy_runtime()
"

# Start the FastAPI application
echo "🌟 Starting FastAPI server..."
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
