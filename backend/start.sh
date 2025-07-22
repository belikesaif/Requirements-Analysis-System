#!/bin/bash

# Production startup script for Render deployment
echo "Starting NLP Requirements Analysis System..."

# Setup SpaCy model
echo "Setting up SpaCy model..."
python -c "
import spacy
import sys

try:
    # Try to load the model
    nlp = spacy.load('en_core_web_sm')
    print('SpaCy model en_core_web_sm loaded successfully')
except OSError:
    print('SpaCy model not found, downloading...')
    try:
        # Download the model
        import subprocess
        result = subprocess.run([sys.executable, '-m', 'spacy', 'download', 'en_core_web_sm'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print('SpaCy model downloaded successfully')
        else:
            print(f'SpaCy download failed: {result.stderr}')
            print('Application will use fallback processing')
    except Exception as e:
        print(f'SpaCy setup error: {e}')
        print('Application will use fallback processing')
"

# Start the FastAPI application
echo "Starting FastAPI server..."
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
