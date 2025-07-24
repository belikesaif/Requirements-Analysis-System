#!/usr/bin/env python3
"""
SpaCy validation script - ensures spaCy is properly configured
This script MUST pass before the application can start
"""

import sys
import subprocess

def validate_spacy_installation():
    """Validate that spaCy and the English model are properly installed"""
    print("🔍 Validating spaCy installation...")
    
    try:
        # Test 1: Import spaCy
        print("1️⃣ Testing spaCy import...")
        import spacy
        print("   ✅ spaCy imported successfully")
        
        # Test 2: Load the English model
        print("2️⃣ Testing English model loading...")
        nlp = spacy.load("en_core_web_sm")
        print("   ✅ en_core_web_sm model loaded successfully")
        
        # Test 3: Test basic NLP processing
        print("3️⃣ Testing NLP processing...")
        doc = nlp("The user logs into the system")
        tokens = [token.text for token in doc]
        pos_tags = [token.pos_ for token in doc]
        print(f"   ✅ Processed text into {len(tokens)} tokens")
        print(f"   📝 Tokens: {tokens}")
        print(f"   🏷️  POS tags: {pos_tags}")
        
        # Test 4: Test textacy (if available)
        print("4️⃣ Testing textacy (optional)...")
        try:
            import textacy
            print("   ✅ textacy is available")
            
            # Test textacy functionality
            sent = list(doc.sents)[0]
            triples = list(textacy.extract.subject_verb_object_triples(sent))
            print(f"   📊 Extracted {len(triples)} SVO triples")
            
        except ImportError:
            print("   ⚠️  textacy not available (will use fallback)")
        except Exception as e:
            print(f"   ⚠️  textacy error (will use fallback): {e}")
        
        # Test 5: Test RUPP processor
        print("5️⃣ Testing RUPP processor...")
        sys.path.insert(0, 'app')
        from app.rupp_integration.rupp_processor import NotebookFaithfulRUPPProcessor
        
        processor = NotebookFaithfulRUPPProcessor()
        test_result = processor.generate_snl_from_text("The user logs into the system")
        
        print(f"   ✅ RUPP processor created successfully")
        print(f"   📋 Generated {test_result['sentences_count']} requirements")
        print(f"   👥 Identified actors: {test_result['actors']}")
        
        print("\n🎉 ALL TESTS PASSED! SpaCy is properly configured.")
        return True
        
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        print("\n🔧 FIX: Install spaCy with: pip install spacy")
        return False
        
    except OSError as e:
        print(f"   ❌ Model loading failed: {e}")
        print("\n🔧 FIX: Download model with: python -m spacy download en_core_web_sm")
        return False
        
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        print(f"   📍 Error type: {type(e).__name__}")
        return False

def attempt_spacy_fix():
    """Attempt to fix spaCy installation if validation fails"""
    print("\n🔧 Attempting to fix spaCy installation...")
    
    try:
        # Try to install spaCy
        print("📦 Installing spaCy...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'spacy>=3.7.0'], check=True)
        
        # Try to download the model
        print("📥 Downloading en_core_web_sm model...")
        result = subprocess.run([sys.executable, '-m', 'spacy', 'download', 'en_core_web_sm'], check=False)
        
        if result.returncode != 0:
            print("⚠️ Standard download failed, trying direct URL...")
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', 
                'https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl'
            ], check=True)
        
        print("✅ spaCy fix attempt completed")
        return True
        
    except Exception as e:
        print(f"❌ Fix attempt failed: {e}")
        return False

def main():
    """Main validation function"""
    print("🚀 SpaCy Validation Script")
    print("=" * 50)
    
    # First validation attempt
    if validate_spacy_installation():
        print("\n✅ VALIDATION PASSED - SpaCy is ready!")
        return 0
    
    # Attempt to fix and revalidate
    print("\n⚠️  VALIDATION FAILED - Attempting fix...")
    if attempt_spacy_fix():
        print("\n🔄 Retrying validation after fix...")
        if validate_spacy_installation():
            print("\n✅ VALIDATION PASSED after fix - SpaCy is ready!")
            return 0
    
    print("\n❌ CRITICAL ERROR: SpaCy validation failed!")
    print("🚫 Application cannot start without proper spaCy configuration")
    print("\n📋 Manual fix steps:")
    print("   1. pip install spacy>=3.7.0")
    print("   2. python -m spacy download en_core_web_sm")
    print("   3. python -c 'import spacy; spacy.load(\"en_core_web_sm\")'")
    
    return 1

if __name__ == "__main__":
    exit(main())
