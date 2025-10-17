"""
Quick test to check for import and basic errors
"""
import sys
import os

print("Testing imports...")

try:
    # Test basic imports
    import matplotlib
    print("✓ matplotlib imported")
    
    import seaborn
    print("✓ seaborn imported")
    
    import pandas
    print("✓ pandas imported")
    
    import plotly
    print("✓ plotly imported")
    
    import folium
    print("✓ folium imported")
    
    import spacy
    print("✓ spacy imported")
    
    # Test spacy model
    try:
        nlp = spacy.load('en_core_web_sm')
        print("✓ spacy model loaded")
    except:
        print("✗ spacy model NOT found - run: python -m spacy download en_core_web_sm")
    
    # Test module imports
    sys.path.insert(0, 'src')
    
    from data_collector import YouTubeDataCollector
    print("✓ data_collector imported")
    
    from nlp_analyzer import NLPAnalyzer
    print("✓ nlp_analyzer imported")
    
    from intelligence_aggregator import IntelligenceAggregator
    print("✓ intelligence_aggregator imported")
    
    from visualizer import Visualizer
    print("✓ visualizer imported")
    
    from report_generator import ReportGenerator
    print("✓ report_generator imported")
    
    print("\n✅ All imports successful!")
    print("\nNow test the pipeline:")
    print("python main.py")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
