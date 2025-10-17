"""
Report Generator Module
Creates 1-page PDF summary with visualizations and key findings
"""

import logging
from datetime import datetime
from typing import Dict, Optional
import os

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates PDF summary reports"""
    
    def __init__(self, output_dir: str = "../outputs"):
        """
        Initialize report generator
        
        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Setup styles
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=8,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        )
        
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['BodyText'],
            fontSize=9,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=6,
            alignment=TA_LEFT
        )
    
    def create_summary_report(self, 
                            video_metadata: Dict,
                            distribution: Dict,
                            language_dist: Dict,
                            signal_breakdown: Dict,
                            charts: Dict[str, str],
                            output_path: str):
        """
        Create comprehensive 1-page PDF summary
        
        Args:
            video_metadata: Video metadata dictionary
            distribution: Viewer distribution data
            language_dist: Language distribution
            signal_breakdown: Signal type breakdown
            charts: Dictionary mapping chart names to file paths
            output_path: Output PDF path
        """
        doc = SimpleDocTemplate(output_path, pagesize=letter,
                              topMargin=0.5*inch, bottomMargin=0.5*inch,
                              leftMargin=0.5*inch, rightMargin=0.5*inch)
        
        story = []
        
        # Title
        title = Paragraph("YouTube Viewer Intelligence Report", self.title_style)
        story.append(title)
        story.append(Spacer(1, 0.1*inch))
        
        # Video Information
        video_title = video_metadata.get('title', 'Unknown Video')
        video_id = video_metadata.get('video_id', 'N/A')
        
        video_info = f"""
        <b>Video:</b> {video_title[:80]}...<br/>
        <b>Video ID:</b> {video_id}<br/>
        <b>Views:</b> {video_metadata.get('view_count', 'N/A'):,}<br/>
        <b>Comments Analyzed:</b> {video_metadata.get('comments_analyzed', 'N/A')}<br/>
        <b>Report Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        story.append(Paragraph(video_info, self.body_style))
        story.append(Spacer(1, 0.15*inch))
        
        # Key Findings
        story.append(Paragraph("Key Findings", self.heading_style))
        
        cities_df = distribution.get('cities')
        countries_df = distribution.get('countries')
        
        if cities_df is not None and len(cities_df) > 0:
            top_city = cities_df.iloc[0]
            findings_text = f"""
            • <b>Top City:</b> {top_city['location']} ({top_city['estimated_percentage']:.1f}% estimated viewers, {top_city['confidence_level']} confidence)<br/>
            • <b>Total Cities Identified:</b> {distribution['summary']['total_cities_identified']}<br/>
            • <b>Total Countries Identified:</b> {distribution['summary']['total_countries_identified']}<br/>
            • <b>Primary Signal Types:</b> {', '.join(list(signal_breakdown.keys())[:3])}<br/>
            • <b>Data Quality:</b> Based on {sum(signal_breakdown.values())} geographic signals
            """
        else:
            findings_text = "Insufficient data for geographic analysis."
        
        story.append(Paragraph(findings_text, self.body_style))
        story.append(Spacer(1, 0.15*inch))
        
        # Top 5 Cities Table
        if cities_df is not None and len(cities_df) > 0:
            story.append(Paragraph("Top 5 Cities by Estimated Viewer Distribution", self.heading_style))
            
            table_data = [['Rank', 'City', 'Est. %', 'Mentions', 'Confidence']]
            for idx, row in cities_df.head(5).iterrows():
                table_data.append([
                    str(idx + 1),
                    row['location'],
                    f"{row['estimated_percentage']:.1f}%",
                    str(row['mention_count']),
                    row['confidence_level']
                ])
            
            table = Table(table_data, colWidths=[0.6*inch, 2*inch, 0.8*inch, 0.8*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            
            story.append(table)
            story.append(Spacer(1, 0.15*inch))
        
        # Add chart if available
        if 'cities_bar' in charts and os.path.exists(charts['cities_bar']):
            story.append(Paragraph("Geographic Distribution Visualization", self.heading_style))
            
            # Resize image to fit
            img = Image(charts['cities_bar'], width=6.5*inch, height=4*inch)
            story.append(img)
            story.append(Spacer(1, 0.1*inch))
        
        # Methodology Note
        story.append(Paragraph("Methodology & Confidence Levels", self.heading_style))
        
        methodology = """
        <b>Data Sources:</b> YouTube comments, video metadata, language detection, NER<br/>
        <b>Confidence Scoring:</b><br/>
        • <b>High (0.7-0.9):</b> Direct city mentions, geocoded locations<br/>
        • <b>Medium (0.5-0.7):</b> Country mentions, multiple weak signals<br/>
        • <b>Low (0.3-0.5):</b> Language-based inference, timezone hints<br/>
        <br/>
        <b>Limitations:</b> Estimates based on commenters only (not all viewers). 
        Geographic mentions may not represent actual viewer location. 
        Results should be interpreted as indicative trends, not precise demographics.
        """
        
        story.append(Paragraph(methodology, self.body_style))
        
        # Build PDF
        doc.build(story)
        logger.info(f"PDF report generated: {output_path}")
    
    def create_simple_png_summary(self, 
                                 distribution: Dict,
                                 language_dist: Dict,
                                 charts: Dict[str, str],
                                 output_path: str):
        """
        Create a simple PNG summary by combining existing charts
        
        Args:
            distribution: Viewer distribution data
            language_dist: Language distribution
            charts: Dictionary of chart paths
            output_path: Output PNG path
        """
        import matplotlib.pyplot as plt
        from matplotlib.gridspec import GridSpec
        from PIL import Image as PILImage
        
        fig = plt.figure(figsize=(11, 8.5))
        gs = GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.3)
        
        # Title
        fig.suptitle('YouTube Viewer Intelligence Summary', 
                    fontsize=16, fontweight='bold', y=0.98)
        
        # Load and display charts
        if 'cities_bar' in charts and os.path.exists(charts['cities_bar']):
            ax1 = fig.add_subplot(gs[0, :])
            img = PILImage.open(charts['cities_bar'])
            ax1.imshow(img)
            ax1.axis('off')
            ax1.set_title('Top Cities', fontsize=12, fontweight='bold')
        
        if 'language_pie' in charts and os.path.exists(charts['language_pie']):
            ax2 = fig.add_subplot(gs[1, 0])
            img = PILImage.open(charts['language_pie'])
            ax2.imshow(img)
            ax2.axis('off')
            ax2.set_title('Language Distribution', fontsize=12, fontweight='bold')
        
        if 'countries_bar' in charts and os.path.exists(charts['countries_bar']):
            ax3 = fig.add_subplot(gs[1, 1])
            img = PILImage.open(charts['countries_bar'])
            ax3.imshow(img)
            ax3.axis('off')
            ax3.set_title('Top Countries', fontsize=12, fontweight='bold')
        
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        logger.info(f"PNG summary generated: {output_path}")


if __name__ == "__main__":
    # Example usage
    generator = ReportGenerator()
    
    sample_metadata = {
        'title': 'Sample Video Title',
        'video_id': 'ggJg6CcKtZE',
        'view_count': 1000000,
        'comments_analyzed': 500
    }
    
    sample_distribution = {
        'cities': None,
        'countries': None,
        'summary': {
            'total_cities_identified': 50,
            'total_countries_identified': 25
        }
    }
    
    sample_charts = {}
    
    # generator.create_summary_report(sample_metadata, sample_distribution, {}, {}, sample_charts, 
    #                                '../outputs/test_report.pdf')
