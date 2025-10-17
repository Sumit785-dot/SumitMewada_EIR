"""
Visualization Module
Creates charts, maps, and visual summaries of viewer intelligence
"""

import logging
from typing import Dict, List, Optional
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import folium
from folium.plugins import HeatMap

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set professional style for better readability
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 10)
plt.rcParams['font.size'] = 12
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['xtick.labelsize'] = 11
plt.rcParams['ytick.labelsize'] = 11
plt.rcParams['legend.fontsize'] = 11
plt.rcParams['figure.titlesize'] = 18


class Visualizer:
    """Creates visualizations for viewer intelligence data"""
    
    def __init__(self, output_dir: str = "../outputs"):
        """
        Initialize visualizer
        
        Args:
            output_dir: Directory to save visualizations
        """
        self.output_dir = output_dir
    
    def plot_top_cities_bar(self, cities_df: pd.DataFrame, top_n: int = 10, 
                           save_path: Optional[str] = None) -> plt.Figure:
        """
        Create horizontal bar chart of top cities
        
        Args:
            cities_df: DataFrame with city data
            top_n: Number of cities to show
            save_path: Path to save figure
            
        Returns:
            Matplotlib figure
        """
        df = cities_df.head(top_n).copy()
        
        # Create color map based on confidence
        colors = df['confidence_level'].map({
            'High': '#2ecc71',
            'Medium': '#f39c12',
            'Low': '#e74c3c'
        })
        
        fig, ax = plt.subplots(figsize=(14, 10))
        
        bars = ax.barh(df['location'], df['estimated_percentage'], color=colors, 
                      edgecolor='black', linewidth=1.2, alpha=0.85)
        
        ax.set_xlabel('Estimated Viewer Percentage (%)', fontsize=16, fontweight='bold', labelpad=10)
        ax.set_ylabel('City', fontsize=16, fontweight='bold', labelpad=10)
        ax.set_title(f'Top {top_n} Cities by Estimated Viewer Distribution', 
                    fontsize=18, fontweight='bold', pad=25)
        
        # Add grid for better readability
        ax.grid(True, axis='x', alpha=0.3, linestyle='--', linewidth=0.8)
        ax.set_axisbelow(True)
        
        # Add percentage labels on bars with larger font
        for i, (bar, pct) in enumerate(zip(bars, df['estimated_percentage'])):
            width = bar.get_width()
            ax.text(width + 0.8, bar.get_y() + bar.get_height()/2, 
                   f'{pct:.1f}%', ha='left', va='center', fontsize=12, fontweight='bold')
        
        # Add legend for confidence levels with larger font
        high_patch = mpatches.Patch(color='#2ecc71', label='High Confidence', alpha=0.85)
        med_patch = mpatches.Patch(color='#f39c12', label='Medium Confidence', alpha=0.85)
        low_patch = mpatches.Patch(color='#e74c3c', label='Low Confidence', alpha=0.85)
        ax.legend(handles=[high_patch, med_patch, low_patch], loc='lower right', 
                 fontsize=12, framealpha=0.9, edgecolor='black')
        
        ax.invert_yaxis()
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Bar chart saved to: {save_path}")
        
        return fig
    
    def plot_language_distribution_pie(self, language_dist: Dict, 
                                       save_path: Optional[str] = None) -> plt.Figure:
        """
        Create pie chart of language distribution
        
        Args:
            language_dist: Dictionary with language distribution
            save_path: Path to save figure
            
        Returns:
            Matplotlib figure
        """
        # Prepare data
        languages = []
        percentages = []
        
        for lang, data in sorted(language_dist.items(), 
                                key=lambda x: x[1]['percentage'], 
                                reverse=True)[:10]:
            languages.append(lang)
            percentages.append(data['percentage'])
        
        # Create pie chart with better styling and no overlapping labels
        fig, ax = plt.subplots(figsize=(14, 10))
        
        colors = sns.color_palette('Set3', len(languages))
        
        # Create pie with labels outside to avoid overlap
        wedges, texts, autotexts = ax.pie(
            percentages, 
            labels=languages, 
            autopct='%1.1f%%',
            colors=colors, 
            startangle=90,
            textprops={'fontsize': 12, 'weight': 'bold'},
            explode=[0.08] * len(languages),  # More separation for clarity
            shadow=True, 
            pctdistance=0.85,
            labeldistance=1.15  # Push labels further out to avoid overlap
        )
        
        # Enhance text for better readability - labels outside
        for text in texts:
            text.set_fontsize(13)
            text.set_weight('bold')
            text.set_color('#2c3e50')  # Dark color for better contrast
        
        # Percentage text inside slices
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(11)
            autotext.set_bbox(dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.3))
        
        ax.set_title('Language Distribution in Comments', fontsize=20, fontweight='bold', pad=30)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Pie chart saved to: {save_path}")
        
        return fig
    
    def plot_country_distribution(self, countries_df: pd.DataFrame, top_n: int = 15,
                                 save_path: Optional[str] = None) -> plt.Figure:
        """
        Create bar chart of country distribution
        
        Args:
            countries_df: DataFrame with country data
            top_n: Number of countries to show
            save_path: Path to save figure
            
        Returns:
            Matplotlib figure
        """
        df = countries_df.head(top_n).copy()
        
        fig, ax = plt.subplots(figsize=(14, 10))
        
        colors = sns.color_palette('viridis', len(df))
        bars = ax.bar(range(len(df)), df['estimated_percentage'], color=colors, 
                     edgecolor='black', linewidth=1.2, alpha=0.85)
        
        ax.set_xlabel('Country', fontsize=16, fontweight='bold', labelpad=10)
        ax.set_ylabel('Estimated Viewer Percentage (%)', fontsize=16, fontweight='bold', labelpad=10)
        ax.set_title(f'Top {top_n} Countries by Estimated Viewer Distribution', 
                    fontsize=18, fontweight='bold', pad=25)
        
        # Add grid for better readability
        ax.grid(True, axis='y', alpha=0.3, linestyle='--', linewidth=0.8)
        ax.set_axisbelow(True)
        
        ax.set_xticks(range(len(df)))
        ax.set_xticklabels(df['location'], rotation=45, ha='right', fontsize=12, fontweight='bold')
        
        # Add percentage labels with larger font
        for bar, pct in zip(bars, df['estimated_percentage']):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + 0.8,
                   f'{pct:.1f}%', ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Country chart saved to: {save_path}")
        
        return fig
    
    def create_interactive_map(self, cities_df: pd.DataFrame, nlp_analyzer,
                              save_path: Optional[str] = None) -> folium.Map:
        """
        Create interactive map with city markers
        
        Args:
            cities_df: DataFrame with city data
            nlp_analyzer: NLPAnalyzer instance for geocoding
            save_path: Path to save HTML map
            
        Returns:
            Folium map object
        """
        # Create base map
        m = folium.Map(location=[20, 0], zoom_start=2, tiles='OpenStreetMap')
        
        # Geocode cities and add markers
        for idx, row in cities_df.head(20).iterrows():
            city = row['location']
            geocoded = nlp_analyzer.geocode_location(city)
            
            if geocoded:
                lat = geocoded['latitude']
                lon = geocoded['longitude']
                
                # Determine marker color based on confidence
                color_map = {
                    'High': 'green',
                    'Medium': 'orange',
                    'Low': 'red'
                }
                color = color_map.get(row['confidence_level'], 'blue')
                
                # Create popup text with better formatting
                popup_text = f"""
                <div style="font-family: Arial; font-size: 14px;">
                    <h4 style="margin: 5px 0; color: #2c3e50;">{city}</h4>
                    <p style="margin: 3px 0;"><b>Estimated:</b> {row['estimated_percentage']:.1f}%</p>
                    <p style="margin: 3px 0;"><b>Mentions:</b> {row['mention_count']}</p>
                    <p style="margin: 3px 0;"><b>Confidence:</b> <span style="color: {color};">{row['confidence_level']}</span></p>
                </div>
                """
                
                # Add marker
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=row['estimated_percentage'] / 2 + 5,
                    popup=folium.Popup(popup_text, max_width=200),
                    color=color,
                    fill=True,
                    fillColor=color,
                    fillOpacity=0.6,
                    weight=2
                ).add_to(m)
        
        if save_path:
            m.save(save_path)
            logger.info(f"Interactive map saved to: {save_path}")
        
        return m
    
    def create_plotly_choropleth(self, countries_df: pd.DataFrame,
                                save_path: Optional[str] = None) -> go.Figure:
        """
        Create interactive choropleth map of countries
        
        Args:
            countries_df: DataFrame with country data
            save_path: Path to save HTML
            
        Returns:
            Plotly figure
        """
        # Map country names to ISO codes (simplified - would need full mapping)
        try:
            import pycountry
            PYCOUNTRY_AVAILABLE = True
        except ImportError:
            PYCOUNTRY_AVAILABLE = False
            logger.warning("pycountry not available. Choropleth map will use country names.")
        
        iso_codes = []
        for country in countries_df['location']:
            if PYCOUNTRY_AVAILABLE:
                try:
                    country_obj = pycountry.countries.search_fuzzy(country)[0]
                    iso_codes.append(country_obj.alpha_3)
                except:
                    iso_codes.append(None)
            else:
                # Fallback: use country names directly (limited functionality)
                iso_codes.append(country)
        
        countries_df['iso_code'] = iso_codes
        
        fig = px.choropleth(
            countries_df,
            locations='iso_code',
            color='estimated_percentage',
            hover_name='location',
            hover_data={
                'estimated_percentage': ':.1f',
                'mention_count': True,
                'confidence_level': True,
                'iso_code': False
            },
            color_continuous_scale='Viridis',
            labels={'estimated_percentage': 'Viewer %'}
        )
        
        fig.update_layout(
            title={
                'text': 'Estimated Viewer Distribution by Country',
                'font': {'size': 24, 'family': 'Arial, sans-serif', 'color': '#2c3e50'},
                'x': 0.5,
                'xanchor': 'center'
            },
            geo=dict(
                showframe=False, 
                showcoastlines=True, 
                projection_type='natural earth',
                bgcolor='rgba(240,240,240,0.5)'
            ),
            height=700,
            font=dict(size=14, family='Arial, sans-serif')
        )
        
        if save_path:
            fig.write_html(save_path)
            logger.info(f"Choropleth map saved to: {save_path}")
        
        return fig
    
    def create_signal_breakdown_chart(self, signal_breakdown: Dict,
                                     save_path: Optional[str] = None) -> plt.Figure:
        """
        Create chart showing breakdown of signal types
        
        Args:
            signal_breakdown: Dictionary with signal counts
            save_path: Path to save figure
            
        Returns:
            Matplotlib figure
        """
        signals = list(signal_breakdown.keys())
        counts = list(signal_breakdown.values())
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        colors = sns.color_palette('Set2', len(signals))
        bars = ax.bar(signals, counts, color=colors, edgecolor='black', 
                     linewidth=1.2, alpha=0.85)
        
        ax.set_xlabel('Signal Type', fontsize=16, fontweight='bold', labelpad=10)
        ax.set_ylabel('Count', fontsize=16, fontweight='bold', labelpad=10)
        ax.set_title('Geographic Signal Types Used in Analysis', 
                    fontsize=18, fontweight='bold', pad=25)
        
        # Add grid for better readability
        ax.grid(True, axis='y', alpha=0.3, linestyle='--', linewidth=0.8)
        ax.set_axisbelow(True)
        
        plt.xticks(rotation=45, ha='right', fontsize=12, fontweight='bold')
        
        # Add count labels with larger font
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + max(counts)*0.02,
                   str(count), ha='center', va='bottom', fontsize=13, fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Signal breakdown chart saved to: {save_path}")
        
        return fig


if __name__ == "__main__":
    # Example usage
    visualizer = Visualizer()
    
    # Create sample data
    sample_cities = pd.DataFrame({
        'location': ['New York', 'London', 'Tokyo', 'Paris', 'Mumbai'],
        'estimated_percentage': [25.5, 18.3, 15.2, 12.1, 10.5],
        'mention_count': [45, 32, 28, 21, 18],
        'confidence_level': ['High', 'High', 'Medium', 'Medium', 'Low']
    })
    
    visualizer.plot_top_cities_bar(sample_cities, save_path='../outputs/test_cities.png')
