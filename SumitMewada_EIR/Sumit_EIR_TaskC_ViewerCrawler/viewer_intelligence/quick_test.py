"""Quick test to identify errors"""
import sys
import os

print("Testing basic imports...")

try:
    print("1. Testing matplotlib...")
    import matplotlib
    print("   ✓ matplotlib OK")
    
    print("2. Testing pandas...")
    import pandas
    print("   ✓ pandas OK")
    
    print("3. Testing langdetect...")
    import langdetect
    print("   ✓ langdetect OK")
    
    print("4. Testing geotext...")
    import geotext
    print("   ✓ geotext OK")
    
    print("5. Testing spacy (optional)...")
    try:
        import spacy
        print("   ✓ spacy available")
        try:
            nlp = spacy.load('en_core_web_sm')
            print("   ✓ spacy model loaded")
        except:
            print("   ⚠ spacy model not found (will use GeoText instead)")
    except Exception as e:
        print(f"   ⚠ spacy not available: {str(e)[:50]}... (will use GeoText instead)")
    
    print("\n6. Testing project modules...")
    sys.path.insert(0, 'src')
    
    from data_collector import YouTubeDataCollector
    print("   ✓ data_collector OK")
    
    from nlp_analyzer import NLPAnalyzer
    print("   ✓ nlp_analyzer OK")
    
    from intelligence_aggregator import IntelligenceAggregator
    print("   ✓ intelligence_aggregator OK")
    
    from visualizer import Visualizer
    print("   ✓ visualizer OK")
    
    from report_generator import ReportGenerator
    print("   ✓ report_generator OK")
    
    print("\n✅ ALL TESTS PASSED!")
    print("\nNow you can run: python main.py")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()
    print("\n" + "="*80)
    print("SOLUTION:")
    print("="*80)
    
    if "spacy" in str(e).lower():
        print("spaCy issue detected. The project will work without spaCy.")
        print("It will use GeoText for location detection instead.")
    elif "module" in str(e).lower():
        print("Missing module. Install with:")
        print("pip install -r requirements.txt")
    else:
        print("Unknown error. Please share this output.")
