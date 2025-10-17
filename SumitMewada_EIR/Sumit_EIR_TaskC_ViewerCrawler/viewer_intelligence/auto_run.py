"""
Auto-run script - No user input needed
"""
import os
import sys
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')
os.environ['PYTHONWARNINGS'] = 'ignore'

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("=" * 80)
print("YOUTUBE VIEWER INTELLIGENCE PIPELINE - AUTO RUN")
print("=" * 80)
print()

# Default configuration
VIDEO_URL = "https://www.youtube.com/watch?v=ggJg6CcKtZE"
MAX_COMMENTS = 1000
USE_CACHE = True

print(f"Video URL: {VIDEO_URL}")
print(f"Max comments: {MAX_COMMENTS}")
print(f"Using cache: {USE_CACHE}")
print()

try:
    # Import pipeline class
    from main import ViewerIntelligencePipeline
    
    # Create and run pipeline
    print("Initializing pipeline...")
    pipeline = ViewerIntelligencePipeline(VIDEO_URL)
    
    print("Running pipeline...")
    print()
    pipeline.run(max_comments=MAX_COMMENTS, use_cache=USE_CACHE)
    
    print()
    print("=" * 80)
    print("✅ PIPELINE COMPLETED!")
    print("=" * 80)
    
except Exception as e:
    print()
    print("=" * 80)
    print(f"❌ ERROR: {e}")
    print("=" * 80)
    
    import traceback
    print("\nFull error details:")
    traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("QUICK FIX:")
    print("=" * 80)
    
    error_msg = str(e).lower()
    
    if "spacy" in error_msg or "pydantic" in error_msg:
        print("spaCy issue - but project should still work with GeoText")
        print("\nTry: pip uninstall spacy -y")
        print("Then run again: python auto_run.py")
    elif "no module" in error_msg:
        print("Missing package detected")
        print("\nTry: pip install -r requirements.txt")
    else:
        print("Unknown error - check the traceback above")
    
    sys.exit(1)
