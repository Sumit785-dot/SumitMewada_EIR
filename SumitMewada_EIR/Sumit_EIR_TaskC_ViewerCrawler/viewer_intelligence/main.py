"""
Main Pipeline Script
Orchestrates the complete viewer intelligence analysis workflow
"""

import os
import sys
import json
import logging
import time
import webbrowser
import subprocess
import platform
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_collector import YouTubeDataCollector
from nlp_analyzer import NLPAnalyzer
from intelligence_aggregator import IntelligenceAggregator
from visualizer import Visualizer
from report_generator import ReportGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ViewerIntelligencePipeline:
    """Complete pipeline for YouTube viewer intelligence analysis"""
    
    def __init__(self, video_url: str, output_dir: str = "outputs"):
        """
        Initialize pipeline
        
        Args:
            video_url: YouTube video URL
            output_dir: Directory for outputs
        """
        self.video_url = video_url
        self.output_dir = output_dir
        
        # Create directory structure
        self.dirs = {
            'raw': os.path.join('data', 'raw'),
            'processed': os.path.join('data', 'processed'),
            'cache': os.path.join('data', 'cache'),
            'outputs': output_dir,
            'charts': os.path.join(output_dir, 'charts')
        }
        
        for dir_path in self.dirs.values():
            os.makedirs(dir_path, exist_ok=True)
        
        # Initialize components
        self.collector = YouTubeDataCollector()
        self.nlp_analyzer = NLPAnalyzer()
        self.aggregator = IntelligenceAggregator()
        self.visualizer = Visualizer(output_dir=self.dirs['charts'])
        self.report_generator = ReportGenerator(output_dir=self.dirs['outputs'])
        
        logger.info(f"Pipeline initialized for video: {video_url}")
    
    def step1_collect_data(self, max_comments: int = 1000, use_cache: bool = True):
        """
        Step 1: Collect video data and comments
        
        Args:
            max_comments: Maximum number of comments to collect
            use_cache: Use cached data if available
        """
        logger.info("=" * 80)
        logger.info("STEP 1: DATA COLLECTION")
        logger.info("=" * 80)
        
        cache_path = os.path.join(self.dirs['cache'], 'video_data.json')
        
        # Check cache
        if use_cache and os.path.exists(cache_path):
            logger.info(f"Loading cached data from: {cache_path}")
            with open(cache_path, 'r', encoding='utf-8') as f:
                self.raw_data = json.load(f)
            logger.info(f"Loaded {len(self.raw_data.get('comments', []))} cached comments")
        else:
            # Collect fresh data
            logger.info("Collecting fresh data from YouTube...")
            self.raw_data = self.collector.collect_all_data(self.video_url, max_comments)
            
            # Save to cache
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(self.raw_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Data cached to: {cache_path}")
        
        # Save raw data
        raw_path = os.path.join(self.dirs['raw'], 'video_data.json')
        with open(raw_path, 'w', encoding='utf-8') as f:
            json.dump(self.raw_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✓ Data collection complete: {len(self.raw_data.get('comments', []))} comments")
    
    def step2_analyze_comments(self):
        """Step 2: Perform NLP analysis on comments"""
        logger.info("=" * 80)
        logger.info("STEP 2: NLP ANALYSIS")
        logger.info("=" * 80)
        
        comments = self.raw_data.get('comments', [])
        
        if not comments:
            logger.warning("No comments to analyze!")
            self.analyses_df = None
            return
        
        # Analyze all comments
        self.analyses_df = self.nlp_analyzer.analyze_all_comments(comments)
        
        # Save analyses
        analyses_path = os.path.join(self.dirs['processed'], 'comment_analyses.csv')
        self.analyses_df.to_csv(analyses_path, index=False)
        logger.info(f"Analyses saved to: {analyses_path}")
        
        # Get language distribution
        self.language_dist = self.nlp_analyzer.get_language_distribution(self.analyses_df)
        
        # Get location mentions
        self.location_mentions = self.nlp_analyzer.get_location_mentions(self.analyses_df)
        
        logger.info(f"✓ NLP analysis complete")
        logger.info(f"  - Languages detected: {len(self.language_dist)}")
        logger.info(f"  - Cities mentioned: {len(self.location_mentions['cities'])}")
        logger.info(f"  - Countries mentioned: {len(self.location_mentions['countries'])}")
    
    def step3_aggregate_intelligence(self):
        """Step 3: Aggregate signals and estimate viewer distribution"""
        logger.info("=" * 80)
        logger.info("STEP 3: INTELLIGENCE AGGREGATION")
        logger.info("=" * 80)
        
        if self.analyses_df is None:
            logger.warning("No analyses available for aggregation!")
            return
        
        # Process all analyses
        self.aggregator.process_all_analyses(self.analyses_df, self.nlp_analyzer)
        
        # Get distribution estimates
        self.distribution = self.aggregator.estimate_viewer_distribution(top_n=50)
        
        # Get signal breakdown
        self.signal_breakdown = self.aggregator.get_signal_breakdown()
        
        # Export results
        export_path = os.path.join(self.dirs['processed'], 'distribution.csv')
        self.aggregator.export_results(export_path)
        
        logger.info(f"✓ Intelligence aggregation complete")
        logger.info(f"  - Top city: {self.distribution['summary']['top_city']}")
        logger.info(f"  - Top country: {self.distribution['summary']['top_country']}")
        logger.info(f"  - Total signals: {sum(self.signal_breakdown.values())}")
    
    def step4_create_visualizations(self):
        """Step 4: Create visualizations"""
        logger.info("=" * 80)
        logger.info("STEP 4: VISUALIZATION")
        logger.info("=" * 80)
        
        self.chart_paths = {}
        
        # Cities bar chart
        if len(self.distribution['cities']) > 0:
            path = os.path.join(self.dirs['charts'], 'top_cities_bar.png')
            self.visualizer.plot_top_cities_bar(
                self.distribution['cities'], 
                top_n=10, 
                save_path=path
            )
            self.chart_paths['cities_bar'] = path
        
        # Language pie chart
        if self.language_dist:
            path = os.path.join(self.dirs['charts'], 'language_distribution_pie.png')
            self.visualizer.plot_language_distribution_pie(
                self.language_dist,
                save_path=path
            )
            self.chart_paths['language_pie'] = path
        
        # Countries bar chart
        if len(self.distribution['countries']) > 0:
            path = os.path.join(self.dirs['charts'], 'top_countries_bar.png')
            self.visualizer.plot_country_distribution(
                self.distribution['countries'],
                top_n=15,
                save_path=path
            )
            self.chart_paths['countries_bar'] = path
        
        # Signal breakdown
        if self.signal_breakdown:
            path = os.path.join(self.dirs['charts'], 'signal_breakdown.png')
            self.visualizer.create_signal_breakdown_chart(
                self.signal_breakdown,
                save_path=path
            )
            self.chart_paths['signal_breakdown'] = path
        
        # Interactive map
        if len(self.distribution['cities']) > 0:
            path = os.path.join(self.dirs['charts'], 'interactive_map.html')
            self.visualizer.create_interactive_map(
                self.distribution['cities'],
                self.nlp_analyzer,
                save_path=path
            )
            self.chart_paths['map'] = path
        
        # Choropleth map
        if len(self.distribution['countries']) > 0:
            path = os.path.join(self.dirs['charts'], 'choropleth_map.html')
            try:
                self.visualizer.create_plotly_choropleth(
                    self.distribution['countries'],
                    save_path=path
                )
                self.chart_paths['choropleth'] = path
            except Exception as e:
                logger.warning(f"Could not create choropleth: {e}")
        
        logger.info(f"✓ Visualizations created: {len(self.chart_paths)} charts")
    
    def step5_generate_report(self):
        """Step 5: Generate final report"""
        logger.info("=" * 80)
        logger.info("STEP 5: REPORT GENERATION")
        logger.info("=" * 80)
        
        # Prepare metadata
        metadata = self.raw_data.get('metadata', {})
        metadata['comments_analyzed'] = len(self.raw_data.get('comments', []))
        
        # Generate PDF report
        pdf_path = os.path.join(self.dirs['outputs'], 'viewer_intelligence_report.pdf')
        self.report_generator.create_summary_report(
            video_metadata=metadata,
            distribution=self.distribution,
            language_dist=self.language_dist,
            signal_breakdown=self.signal_breakdown,
            charts=self.chart_paths,
            output_path=pdf_path
        )
        
        # Generate PNG summary
        png_path = os.path.join(self.dirs['outputs'], 'viewer_intelligence_summary.png')
        self.report_generator.create_simple_png_summary(
            distribution=self.distribution,
            language_dist=self.language_dist,
            charts=self.chart_paths,
            output_path=png_path
        )
        
        logger.info(f"✓ Reports generated:")
        logger.info(f"  - PDF: {pdf_path}")
        logger.info(f"  - PNG: {png_path}")
    
    def run(self, max_comments: int = 1000, use_cache: bool = True):
        """
        Run complete pipeline
        
        Args:
            max_comments: Maximum comments to collect
            use_cache: Use cached data if available
        """
        start_time = datetime.now()
        logger.info("=" * 80)
        logger.info("YOUTUBE VIEWER INTELLIGENCE PIPELINE")
        logger.info("=" * 80)
        logger.info(f"Video URL: {self.video_url}")
        logger.info(f"Start time: {start_time}")
        logger.info("")
        
        try:
            # Run all steps
            self.step1_collect_data(max_comments, use_cache)
            self.step2_analyze_comments()
            self.step3_aggregate_intelligence()
            self.step4_create_visualizations()
            self.step5_generate_report()
            
            # Summary
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info("")
            logger.info("=" * 80)
            logger.info("PIPELINE COMPLETE")
            logger.info("=" * 80)
            logger.info(f"Duration: {duration:.2f} seconds")
            logger.info(f"Output directory: {self.dirs['outputs']}")
            logger.info("")
            logger.info("Key outputs:")
            logger.info(f"  - PDF Report: {os.path.join(self.dirs['outputs'], 'viewer_intelligence_report.pdf')}")
            logger.info(f"  - PNG Summary: {os.path.join(self.dirs['outputs'], 'viewer_intelligence_summary.png')}")
            logger.info(f"  - Charts: {self.dirs['charts']}")
            logger.info(f"  - Data: {self.dirs['processed']}")
            logger.info("=" * 80)
            
            # Auto-open outputs
            self._open_outputs()
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            raise
    
    def _open_outputs(self):
        """Automatically open all generated outputs"""
        logger.info("\n🚀 Opening outputs...")
        
        try:
            # Open PDF report
            pdf_path = os.path.join(self.dirs['outputs'], 'viewer_intelligence_report.pdf')
            if os.path.exists(pdf_path):
                self._open_file(pdf_path)
                logger.info(f"✓ Opened PDF report")
            
            # Open PNG summary
            png_path = os.path.join(self.dirs['outputs'], 'viewer_intelligence_summary.png')
            if os.path.exists(png_path):
                self._open_file(png_path)
                logger.info(f"✓ Opened PNG summary")
            
            # Open interactive maps in browser
            interactive_map = os.path.join(self.dirs['charts'], 'interactive_map.html')
            if os.path.exists(interactive_map):
                webbrowser.open('file://' + os.path.abspath(interactive_map))
                logger.info(f"✓ Opened interactive map in browser")
            
            choropleth_map = os.path.join(self.dirs['charts'], 'choropleth_map.html')
            if os.path.exists(choropleth_map):
                webbrowser.open('file://' + os.path.abspath(choropleth_map))
                logger.info(f"✓ Opened choropleth map in browser")
            
            # Open charts folder
            if os.path.exists(self.dirs['charts']):
                self._open_file(self.dirs['charts'])
                logger.info(f"✓ Opened charts folder")
            
            logger.info("\n✅ All outputs opened successfully!")
            
        except Exception as e:
            logger.warning(f"Could not auto-open some outputs: {e}")
    
    def _open_file(self, filepath):
        """Open file with default application based on OS"""
        filepath = os.path.abspath(filepath)
        
        if platform.system() == 'Windows':
            os.startfile(filepath)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.run(['open', filepath])
        else:  # Linux
            subprocess.run(['xdg-open', filepath])


def main():
    """Main entry point"""
    # Get video URL from user input
    print("=" * 80)
    print("YOUTUBE VIEWER INTELLIGENCE PIPELINE")
    print("=" * 80)
    VIDEO_URL = input("Enter YouTube video URL: ").strip()
    
    # Validate URL
    if not VIDEO_URL:
        print("Error: No URL provided!")
        return
    
    if "youtube.com" not in VIDEO_URL and "youtu.be" not in VIDEO_URL:
        print("Error: Invalid YouTube URL!")
        return
    
    # Configuration
    MAX_COMMENTS = 1000
    USE_CACHE = True  # Set to False to force fresh data collection
    AUTO_OPEN = True  # Set to False to disable auto-opening outputs
    
    print(f"\nProcessing video: {VIDEO_URL}")
    print(f"Max comments: {MAX_COMMENTS}")
    print(f"Using cache: {USE_CACHE}")
    print(f"Auto-open outputs: {AUTO_OPEN}\n")
    
    # Run pipeline
    pipeline = ViewerIntelligencePipeline(VIDEO_URL)
    pipeline.run(max_comments=MAX_COMMENTS, use_cache=USE_CACHE)
    
    if AUTO_OPEN:
        print("\n" + "=" * 80)
        print("📂 All outputs have been opened automatically!")
        print("Check your browser and file viewer for results.")
        print("=" * 80)


if __name__ == "__main__":
    main()
