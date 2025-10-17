"""
Cleanup Script - Delete old outputs
"""
import os
import shutil

def cleanup_outputs():
    """Delete all old output files"""
    print("🧹 Cleaning up old outputs...")
    
    # Delete PDF report
    pdf_path = "outputs/viewer_intelligence_report.pdf"
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
        print(f"✓ Deleted: {pdf_path}")
    
    # Delete PNG summary
    png_path = "outputs/viewer_intelligence_summary.png"
    if os.path.exists(png_path):
        os.remove(png_path)
        print(f"✓ Deleted: {png_path}")
    
    # Delete all charts
    charts_dir = "outputs/charts"
    if os.path.exists(charts_dir):
        for file in os.listdir(charts_dir):
            file_path = os.path.join(charts_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"✓ Deleted: {file_path}")
    
    # Delete processed data
    processed_dir = "data/processed"
    if os.path.exists(processed_dir):
        for file in os.listdir(processed_dir):
            file_path = os.path.join(processed_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"✓ Deleted: {file_path}")
    
    print("\n✅ All old outputs cleaned successfully!")
    print("\nNow run: python main.py")

if __name__ == "__main__":
    cleanup_outputs()
