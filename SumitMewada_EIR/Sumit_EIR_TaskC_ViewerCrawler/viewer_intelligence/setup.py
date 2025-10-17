"""
Setup Script
Automates environment setup and dependency installation
"""

import os
import sys
import subprocess
import platform


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"→ {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"  Error: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible"""
    print_header("Checking Python Version")
    
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("✗ Python 3.8 or higher is required!")
        return False
    
    print("✓ Python version is compatible")
    return True


def create_directories():
    """Create necessary directories"""
    print_header("Creating Directory Structure")
    
    dirs = [
        'data/raw',
        'data/processed',
        'data/cache',
        'outputs',
        'outputs/charts',
        'src'
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"✓ Created: {dir_path}")
    
    return True


def install_dependencies():
    """Install Python dependencies"""
    print_header("Installing Python Dependencies")
    
    if not os.path.exists('requirements.txt'):
        print("✗ requirements.txt not found!")
        return False
    
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing packages from requirements.txt"
    )


def download_spacy_model():
    """Download spaCy language model"""
    print_header("Downloading spaCy Model")
    
    return run_command(
        f"{sys.executable} -m spacy download en_core_web_sm",
        "Downloading en_core_web_sm model"
    )


def setup_env_file():
    """Setup .env file"""
    print_header("Setting Up Environment File")
    
    if os.path.exists('.env'):
        print("✓ .env file already exists")
        return True
    
    if os.path.exists('.env.example'):
        # Copy example to .env
        with open('.env.example', 'r') as f:
            content = f.read()
        
        with open('.env', 'w') as f:
            f.write(content)
        
        print("✓ Created .env file from .env.example")
        print("\n⚠️  IMPORTANT: Edit .env and add your YouTube API key!")
        print("   Get your key from: https://console.cloud.google.com/apis/credentials")
        return True
    else:
        print("✗ .env.example not found!")
        return False


def verify_installation():
    """Verify that key packages are importable"""
    print_header("Verifying Installation")
    
    packages = [
        ('google-api-python-client', 'googleapiclient'),
        ('yt-dlp', 'yt_dlp'),
        ('spacy', 'spacy'),
        ('langdetect', 'langdetect'),
        ('geotext', 'geotext'),
        ('geopy', 'geopy'),
        ('pandas', 'pandas'),
        ('matplotlib', 'matplotlib'),
        ('plotly', 'plotly'),
        ('folium', 'folium'),
        ('reportlab', 'reportlab')
    ]
    
    all_ok = True
    for package_name, import_name in packages:
        try:
            __import__(import_name)
            print(f"✓ {package_name}")
        except ImportError:
            print(f"✗ {package_name} - NOT INSTALLED")
            all_ok = False
    
    # Check spaCy model
    try:
        import spacy
        nlp = spacy.load('en_core_web_sm')
        print(f"✓ spacy model (en_core_web_sm)")
    except:
        print(f"✗ spacy model (en_core_web_sm) - NOT INSTALLED")
        all_ok = False
    
    return all_ok


def print_next_steps():
    """Print next steps for user"""
    print_header("Setup Complete!")
    
    print("Next steps:")
    print("\n1. Configure your YouTube API key:")
    print("   - Edit the .env file")
    print("   - Replace 'your_api_key_here' with your actual API key")
    print("   - Get a key from: https://console.cloud.google.com/apis/credentials")
    
    print("\n2. Run the pipeline:")
    print("   python main.py")
    
    print("\n3. Check outputs:")
    print("   - PDF report: outputs/viewer_intelligence_report.pdf")
    print("   - PNG summary: outputs/viewer_intelligence_summary.png")
    print("   - Charts: outputs/charts/")
    
    print("\n4. Optional: Review cached data")
    print("   - The pipeline can run with cached data if API quota is limited")
    print("   - Set USE_CACHE=True in main.py")
    
    print("\nFor more information, see README.md")
    print("\n" + "=" * 80 + "\n")


def main():
    """Main setup function"""
    print("\n" + "=" * 80)
    print("  YOUTUBE VIEWER INTELLIGENCE CRAWLER - SETUP")
    print("=" * 80)
    
    steps = [
        ("Python Version Check", check_python_version),
        ("Directory Creation", create_directories),
        ("Environment File Setup", setup_env_file),
        ("Dependency Installation", install_dependencies),
        ("spaCy Model Download", download_spacy_model),
        ("Installation Verification", verify_installation)
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        if not step_func():
            failed_steps.append(step_name)
    
    if failed_steps:
        print_header("Setup Incomplete")
        print("The following steps failed:")
        for step in failed_steps:
            print(f"  ✗ {step}")
        print("\nPlease resolve the errors above and run setup again.")
        sys.exit(1)
    else:
        print_next_steps()
        sys.exit(0)


if __name__ == "__main__":
    main()
