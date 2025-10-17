"""
Test Pipeline Script
Tests individual components and the complete pipeline
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_collector import YouTubeDataCollector
from nlp_analyzer import NLPAnalyzer
from intelligence_aggregator import IntelligenceAggregator
from visualizer import Visualizer
from report_generator import ReportGenerator
import pandas as pd


def test_data_collector():
    """Test data collection module"""
    print("\n" + "="*80)
    print("TEST 1: Data Collector")
    print("="*80)
    
    try:
        collector = YouTubeDataCollector()
        
        # Test video ID extraction
        test_urls = [
            "https://www.youtube.com/watch?v=ggJg6CcKtZE",
            "https://youtu.be/ggJg6CcKtZE",
            "ggJg6CcKtZE"
        ]
        
        for url in test_urls:
            video_id = collector.extract_video_id(url)
            assert video_id == "ggJg6CcKtZE", f"Failed to extract video ID from {url}"
            print(f"✓ Extracted video ID from: {url}")
        
        print("✓ Data Collector tests passed")
        return True
    except Exception as e:
        print(f"✗ Data Collector tests failed: {e}")
        return False


def test_nlp_analyzer():
    """Test NLP analysis module"""
    print("\n" + "="*80)
    print("TEST 2: NLP Analyzer")
    print("="*80)
    
    try:
        analyzer = NLPAnalyzer()
        
        # Test language detection
        test_texts = [
            ("Hello, this is a test in English", "en"),
            ("Bonjour, ceci est un test en français", "fr"),
            ("Hola, esto es una prueba en español", "es"),
        ]
        
        for text, expected_lang in test_texts:
            detected_lang, confidence = analyzer.detect_language(text)
            print(f"✓ Detected '{detected_lang}' (expected '{expected_lang}') - confidence: {confidence:.2f}")
        
        # Test location extraction
        test_comment = {
            'comment_id': 'test_001',
            'author': 'TestUser',
            'text': 'Greetings from New York! I love this video. Hello from the USA!',
            'published_at': '2024-01-15T14:30:00Z'
        }
        
        analysis = analyzer.analyze_comment(test_comment)
        print(f"✓ Analyzed comment: {analysis['language']}")
        print(f"  Cities: {analysis['cities_mentioned']}")
        print(f"  Countries: {analysis['countries_mentioned']}")
        
        # Test geocoding (limited to avoid rate limits)
        geocoded = analyzer.geocode_location("New York")
        if geocoded:
            print(f"✓ Geocoded 'New York': {geocoded['latitude']:.2f}, {geocoded['longitude']:.2f}")
        
        print("✓ NLP Analyzer tests passed")
        return True
    except Exception as e:
        print(f"✗ NLP Analyzer tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_intelligence_aggregator():
    """Test intelligence aggregation module"""
    print("\n" + "="*80)
    print("TEST 3: Intelligence Aggregator")
    print("="*80)
    
    try:
        aggregator = IntelligenceAggregator()
        
        # Add test signals
        aggregator.add_signal("New York", "city_mentioned")
        aggregator.add_signal("New York", "city_mentioned")
        aggregator.add_signal("London", "city_mentioned")
        aggregator.add_signal("United States", "country_mentioned", level='country')
        aggregator.add_signal("United Kingdom", "language_to_country", level='country')
        
        # Get distribution
        distribution = aggregator.estimate_viewer_distribution(top_n=10)
        
        print(f"✓ Cities identified: {len(distribution['cities'])}")
        print(f"✓ Countries identified: {len(distribution['countries'])}")
        
        if len(distribution['cities']) > 0:
            top_city = distribution['cities'].iloc[0]
            print(f"✓ Top city: {top_city['location']} ({top_city['estimated_percentage']:.1f}%)")
        
        # Test signal breakdown
        breakdown = aggregator.get_signal_breakdown()
        print(f"✓ Signal types used: {list(breakdown.keys())}")
        
        print("✓ Intelligence Aggregator tests passed")
        return True
    except Exception as e:
        print(f"✗ Intelligence Aggregator tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_visualizer():
    """Test visualization module"""
    print("\n" + "="*80)
    print("TEST 4: Visualizer")
    print("="*80)
    
    try:
        visualizer = Visualizer(output_dir='outputs/test')
        
        # Create sample data
        sample_cities = pd.DataFrame({
            'location': ['New York', 'London', 'Tokyo', 'Paris', 'Mumbai'],
            'estimated_percentage': [25.5, 18.3, 15.2, 12.1, 10.5],
            'mention_count': [45, 32, 28, 21, 18],
            'confidence_level': ['High', 'High', 'Medium', 'Medium', 'Low'],
            'total_score': [22.95, 16.47, 13.68, 10.89, 9.45]
        })
        
        sample_language = {
            'English': {'count': 450, 'percentage': 45.0, 'code': 'en'},
            'Spanish': {'count': 250, 'percentage': 25.0, 'code': 'es'},
            'French': {'count': 150, 'percentage': 15.0, 'code': 'fr'},
            'German': {'count': 100, 'percentage': 10.0, 'code': 'de'},
            'Japanese': {'count': 50, 'percentage': 5.0, 'code': 'ja'}
        }
        
        # Test bar chart
        os.makedirs('outputs/test', exist_ok=True)
        visualizer.plot_top_cities_bar(sample_cities, save_path='outputs/test/test_cities.png')
        print("✓ Created bar chart")
        
        # Test pie chart
        visualizer.plot_language_distribution_pie(sample_language, save_path='outputs/test/test_language.png')
        print("✓ Created pie chart")
        
        print("✓ Visualizer tests passed")
        return True
    except Exception as e:
        print(f"✗ Visualizer tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_report_generator():
    """Test report generation module"""
    print("\n" + "="*80)
    print("TEST 5: Report Generator")
    print("="*80)
    
    try:
        generator = ReportGenerator(output_dir='outputs/test')
        
        # Sample data
        sample_metadata = {
            'title': 'Test Video Title',
            'video_id': 'test123',
            'view_count': 1000000,
            'comments_analyzed': 500
        }
        
        sample_cities = pd.DataFrame({
            'location': ['New York', 'London', 'Tokyo'],
            'estimated_percentage': [30.0, 25.0, 20.0],
            'mention_count': [50, 40, 35],
            'confidence_level': ['High', 'High', 'Medium'],
            'total_score': [27.0, 22.5, 18.0]
        })
        
        sample_distribution = {
            'cities': sample_cities,
            'countries': pd.DataFrame(),
            'summary': {
                'total_cities_identified': 25,
                'total_countries_identified': 15,
                'top_city': 'New York',
                'top_country': 'United States'
            }
        }
        
        sample_language = {
            'English': {'count': 300, 'percentage': 60.0}
        }
        
        sample_signals = {
            'city_mentioned': 120,
            'country_mentioned': 80,
            'language_to_country': 200
        }
        
        # Generate PDF (if charts exist)
        charts = {}
        if os.path.exists('outputs/test/test_cities.png'):
            charts['cities_bar'] = 'outputs/test/test_cities.png'
        
        generator.create_summary_report(
            sample_metadata,
            sample_distribution,
            sample_language,
            sample_signals,
            charts,
            'outputs/test/test_report.pdf'
        )
        print("✓ Created PDF report")
        
        print("✓ Report Generator tests passed")
        return True
    except Exception as e:
        print(f"✗ Report Generator tests failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_complete_pipeline():
    """Test complete pipeline with sample data"""
    print("\n" + "="*80)
    print("TEST 6: Complete Pipeline (Sample Data)")
    print("="*80)
    
    try:
        # Generate sample data first
        print("Generating sample data...")
        from generate_sample_data import generate_sample_data
        import json
        
        sample_data = generate_sample_data(num_comments=50)
        
        os.makedirs('data/cache', exist_ok=True)
        with open('data/cache/test_video_data.json', 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, ensure_ascii=False, indent=2)
        
        print("✓ Sample data generated")
        
        # Run mini pipeline
        analyzer = NLPAnalyzer()
        aggregator = IntelligenceAggregator()
        
        # Analyze comments
        analyses = []
        for comment in sample_data['comments'][:20]:  # Test with 20 comments
            analysis = analyzer.analyze_comment(comment)
            analyses.append(analysis)
        
        analyses_df = pd.DataFrame(analyses)
        print(f"✓ Analyzed {len(analyses_df)} comments")
        
        # Aggregate
        aggregator.process_all_analyses(analyses_df, analyzer)
        distribution = aggregator.estimate_viewer_distribution(top_n=10)
        
        print(f"✓ Distribution calculated")
        print(f"  Cities: {len(distribution['cities'])}")
        print(f"  Countries: {len(distribution['countries'])}")
        
        print("✓ Complete Pipeline test passed")
        return True
    except Exception as e:
        print(f"✗ Complete Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("YOUTUBE VIEWER INTELLIGENCE CRAWLER - TEST SUITE")
    print("="*80)
    
    tests = [
        ("Data Collector", test_data_collector),
        ("NLP Analyzer", test_nlp_analyzer),
        ("Intelligence Aggregator", test_intelligence_aggregator),
        ("Visualizer", test_visualizer),
        ("Report Generator", test_report_generator),
        ("Complete Pipeline", test_complete_pipeline)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The pipeline is ready to use.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
