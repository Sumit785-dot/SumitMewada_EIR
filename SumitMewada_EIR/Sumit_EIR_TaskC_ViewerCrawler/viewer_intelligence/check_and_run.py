"""
Comprehensive Check and Run Script
Checks all dependencies and runs the pipeline
"""
import sys
import os

def check_dependencies():
    """Check if all required packages are installed"""
    print("=" * 80)
    print("CHECKING DEPENDENCIES")
    print("=" * 80)
    
    required_packages = {
        'matplotlib': 'matplotlib',
        'seaborn': 'seaborn',
        'pandas': 'pandas',
        'numpy': 'numpy',
        'plotly': 'plotly',
        'folium': 'folium',
        'spacy': 'spacy',
        'langdetect': 'langdetect',
        'geotext': 'geotext',
        'geopy': 'geopy',
        'reportlab': 'reportlab',
        'PIL': 'Pillow',
        'pycountry': 'pycountry',
        'googleapiclient': 'google-api-python-client',
        'dotenv': 'python-dotenv'
    }
    
    missing = []
    
    for module, package in required_packages.items():
        try:
            __import__(module)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print(f"\nInstall with: pip install {' '.join(missing)}")
        return False
    
    # Check spaCy model
    print("\nChecking spaCy model...")
    try:
        import spacy
        nlp = spacy.load('en_core_web_sm')
        print("✓ spaCy model 'en_core_web_sm' loaded")
    except:
        print("✗ spaCy model 'en_core_web_sm' NOT found")
        print("Install with: python -m spacy download en_core_web_sm")
        return False
    
    print("\n✅ All dependencies installed!")
    return True


def check_project_structure():
    """Check if all required files and folders exist"""
    print("\n" + "=" * 80)
    print("CHECKING PROJECT STRUCTURE")
    print("=" * 80)
    
    required_dirs = ['src', 'data', 'outputs', 'data/cache', 'data/raw', 
                     'data/processed', 'outputs/charts']
    required_files = ['main.py', 'requirements.txt', 'README.md',
                      'src/data_collector.py', 'src/nlp_analyzer.py',
                      'src/intelligence_aggregator.py', 'src/visualizer.py',
                      'src/report_generator.py']
    
    all_good = True
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✓ {dir_path}/")
        else:
            print(f"✗ {dir_path}/ - MISSING")
            os.makedirs(dir_path, exist_ok=True)
            print(f"  → Created {dir_path}/")
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - MISSING")
            all_good = False
    
    if all_good:
        print("\n✅ Project structure is complete!")
    return all_good


def test_imports():
    """Test if all modules can be imported"""
    print("\n" + "=" * 80)
    print("TESTING MODULE IMPORTS")
    print("=" * 80)
    
    sys.path.insert(0, 'src')
    
    modules = [
        'data_collector',
        'nlp_analyzer',
        'intelligence_aggregator',
        'visualizer',
        'report_generator'
    ]
    
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module}.py")
        except Exception as e:
            print(f"✗ {module}.py - ERROR: {e}")
            return False
    
    print("\n✅ All modules imported successfully!")
    return True


def run_pipeline():
    """Run the main pipeline"""
    print("\n" + "=" * 80)
    print("RUNNING PIPELINE")
    print("=" * 80)
    
    # Import and run main
    import main
    main.main()


if __name__ == "__main__":
    print("\n🚀 YOUTUBE VIEWER INTELLIGENCE - COMPREHENSIVE CHECK\n")
    
    # Step 1: Check dependencies
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please install missing packages.")
        sys.exit(1)
    
    # Step 2: Check project structure
    if not check_project_structure():
        print("\n❌ Project structure check failed. Please fix missing files.")
        sys.exit(1)
    
    # Step 3: Test imports
    if not test_imports():
        print("\n❌ Module import test failed. Please check for syntax errors.")
        sys.exit(1)
    
    # Step 4: Run pipeline
    print("\n✅ All checks passed! Starting pipeline...\n")
    try:
        run_pipeline()
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Pipeline failed with error: {e}")
        import traceback
        traceback.print_exc()
