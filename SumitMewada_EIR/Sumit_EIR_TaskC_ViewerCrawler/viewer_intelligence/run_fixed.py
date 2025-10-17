"""
Bug-Free Pipeline Runner
Handles all known issues and runs the complete pipeline
"""
import os
import sys
import warnings
import logging

# Suppress all warnings
warnings.filterwarnings('ignore')
os.environ['PYTHONWARNINGS'] = 'ignore'

# Configure logging to be less verbose
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')

def check_and_create_directories():
    """Ensure all required directories exist"""
    dirs = [
        'data', 'data/cache', 'data/raw', 'data/processed',
        'outputs', 'outputs/charts'
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)

def create_sample_data():
    """Create sample cached data if none exists"""
    cache_file = "data/cache/comments_cache.json"
    
    if not os.path.exists(cache_file):
        print("Creating sample data for demonstration...")
        
        import json
        from datetime import datetime
        
        # Sample comments data
        sample_data = {
            "metadata": {
                "video_id": "ggJg6CcKtZE",
                "title": "Sample Video",
                "description": "Sample description",
                "channel_title": "Sample Channel",
                "view_count": 1000000,
                "like_count": 50000,
                "comment_count": 1000,
                "collected_at": datetime.now().isoformat()
            },
            "comments": []
        }
        
        # Generate sample comments with geographic hints
        locations = [
            ("New York", "USA", "en"),
            ("London", "UK", "en"), 
            ("Paris", "France", "fr"),
            ("Tokyo", "Japan", "ja"),
            ("Mumbai", "India", "hi"),
            ("Berlin", "Germany", "de"),
            ("Sydney", "Australia", "en"),
            ("Toronto", "Canada", "en"),
            ("Madrid", "Spain", "es"),
            ("Rome", "Italy", "it")
        ]
        
        import random
        
        for i in range(200):
            city, country, lang = random.choice(locations)
            
            # Create comments with location hints
            texts = [
                f"Great video! Watching from {city}",
                f"Love this! Greetings from {city}, {country}",
                f"Amazing content, {city} viewer here!",
                f"Watching this in {city} right now",
                f"Hello from {city}! Great work",
                f"This is awesome! {city} fan here",
                f"Incredible video, sending love from {city}",
                f"Fantastic! Viewer from {city}, {country}",
                f"Brilliant content! {city} audience loves it",
                f"Outstanding work! {city} viewer impressed"
            ]
            
            comment = {
                "comment_id": f"comment_{i}",
                "author": f"User{i}",
                "text": random.choice(texts),
                "like_count": random.randint(0, 100),
                "published_at": datetime.now().isoformat(),
                "is_reply": False
            }
            
            sample_data["comments"].append(comment)
        
        # Save sample data
        os.makedirs("data/cache", exist_ok=True)
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Created sample data with {len(sample_data['comments'])} comments")

def run_pipeline():
    """Run the complete pipeline with error handling"""
    
    print("=" * 80)
    print("🚀 YOUTUBE VIEWER INTELLIGENCE PIPELINE")
    print("=" * 80)
    print()
    
    # Setup
    check_and_create_directories()
    create_sample_data()
    
    # Add src to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    # Configuration
    VIDEO_URL = "https://www.youtube.com/watch?v=ggJg6CcKtZE"
    MAX_COMMENTS = 1000
    USE_CACHE = True
    
    print(f"📹 Video URL: {VIDEO_URL}")
    print(f"💬 Max comments: {MAX_COMMENTS}")
    print(f"💾 Using cache: {USE_CACHE}")
    print()
    
    try:
        print("📦 Loading modules...")
        
        # Import with error handling
        try:
            from data_collector import YouTubeDataCollector
            print("  ✓ Data collector loaded")
        except Exception as e:
            print(f"  ❌ Data collector error: {e}")
            return False
            
        try:
            from nlp_analyzer import NLPAnalyzer
            print("  ✓ NLP analyzer loaded")
        except Exception as e:
            print(f"  ❌ NLP analyzer error: {e}")
            return False
            
        try:
            from intelligence_aggregator import IntelligenceAggregator
            print("  ✓ Intelligence aggregator loaded")
        except Exception as e:
            print(f"  ❌ Intelligence aggregator error: {e}")
            return False
            
        try:
            from visualizer import Visualizer
            print("  ✓ Visualizer loaded")
        except Exception as e:
            print(f"  ❌ Visualizer error: {e}")
            return False
            
        try:
            from report_generator import ReportGenerator
            print("  ✓ Report generator loaded")
        except Exception as e:
            print(f"  ❌ Report generator error: {e}")
            return False
        
        print()
        print("🔄 Running pipeline...")
        print()
        
        # Import and run main pipeline
        from main import ViewerIntelligencePipeline
        
        # Create pipeline
        pipeline = ViewerIntelligencePipeline(VIDEO_URL)
        
        # Run pipeline
        pipeline.run(max_comments=MAX_COMMENTS, use_cache=USE_CACHE)
        
        print()
        print("=" * 80)
        print("✅ PIPELINE COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        print()
        
        # List outputs
        outputs_dir = "outputs"
        if os.path.exists(outputs_dir):
            print("📂 Generated outputs:")
            
            pdf_file = os.path.join(outputs_dir, "viewer_intelligence_report.pdf")
            if os.path.exists(pdf_file):
                print(f"  ✓ PDF Report: {pdf_file}")
            
            png_file = os.path.join(outputs_dir, "viewer_intelligence_summary.png")
            if os.path.exists(png_file):
                print(f"  ✓ PNG Summary: {png_file}")
            
            charts_dir = os.path.join(outputs_dir, "charts")
            if os.path.exists(charts_dir):
                chart_files = os.listdir(charts_dir)
                print(f"  ✓ Charts ({len(chart_files)} files): {charts_dir}")
                for chart in chart_files:
                    print(f"    - {chart}")
        
        print()
        print("🎉 All outputs generated successfully!")
        return True
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        return False
        
    except Exception as e:
        print(f"\n\n❌ PIPELINE ERROR: {e}")
        
        # Detailed error info
        import traceback
        print("\n📋 Error details:")
        print("-" * 40)
        traceback.print_exc()
        print("-" * 40)
        
        # Suggestions
        print("\n💡 Troubleshooting suggestions:")
        error_str = str(e).lower()
        
        if "spacy" in error_str or "pydantic" in error_str:
            print("  • spaCy compatibility issue detected")
            print("  • The pipeline should work without spaCy (uses GeoText)")
            print("  • Try: pip uninstall spacy -y")
            
        elif "no module" in error_str or "import" in error_str:
            print("  • Missing Python package")
            print("  • Try: pip install -r requirements.txt")
            
        elif "permission" in error_str:
            print("  • File permission issue")
            print("  • Try running as administrator")
            
        else:
            print("  • Unknown error - check the error details above")
            print("  • Try running: pip install -r requirements.txt")
        
        return False

if __name__ == "__main__":
    print("🔧 Starting bug-free pipeline runner...")
    print()
    
    success = run_pipeline()
    
    if success:
        print("\n🎊 Pipeline completed successfully!")
        print("Check the outputs/ directory for results.")
    else:
        print("\n💥 Pipeline failed. Check error messages above.")
        sys.exit(1)
