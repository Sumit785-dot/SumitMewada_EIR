"""
Intelligence Aggregation Module
Combines signals with confidence scoring to estimate viewer geography
"""

import logging
from typing import Dict, List, Tuple
from collections import defaultdict
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class IntelligenceAggregator:
    """Aggregates multiple signals to estimate viewer demographics"""
    
    # Confidence weights for different signal types
    CONFIDENCE_WEIGHTS = {
        'city_mentioned': 0.9,          # Direct city mention in comment
        'country_mentioned': 0.7,        # Direct country mention
        'geocoded_location': 0.85,       # Successfully geocoded location
        'language_to_country': 0.3,      # Inferred from language
        'timezone_hint': 0.2,            # Inferred from posting time
        'channel_metadata': 0.5,         # From channel's default language/region
    }
    
    def __init__(self):
        """Initialize the aggregator"""
        self.location_scores = defaultdict(lambda: {'score': 0.0, 'signals': [], 'count': 0})
        self.country_scores = defaultdict(lambda: {'score': 0.0, 'signals': [], 'count': 0})
    
    def add_signal(self, location: str, signal_type: str, confidence: float = None, 
                   metadata: Dict = None, level: str = 'city'):
        """
        Add a geographic signal with confidence score
        
        Args:
            location: Location name (city or country)
            signal_type: Type of signal (e.g., 'city_mentioned', 'language_to_country')
            confidence: Override confidence (uses default if None)
            metadata: Additional metadata about the signal
            level: 'city' or 'country'
        """
        if confidence is None:
            confidence = self.CONFIDENCE_WEIGHTS.get(signal_type, 0.5)
        
        signal_info = {
            'type': signal_type,
            'confidence': confidence,
            'metadata': metadata or {}
        }
        
        target = self.location_scores if level == 'city' else self.country_scores
        
        target[location]['score'] += confidence
        target[location]['signals'].append(signal_info)
        target[location]['count'] += 1
    
    def process_comment_analysis(self, analysis: Dict, nlp_analyzer=None):
        """
        Process a single comment analysis and extract signals
        
        Args:
            analysis: Analysis dictionary from NLPAnalyzer
            nlp_analyzer: NLPAnalyzer instance for geocoding
        """
        # City mentions (high confidence)
        for city in analysis.get('cities_mentioned', []):
            self.add_signal(
                city, 
                'city_mentioned',
                metadata={'comment_id': analysis.get('comment_id')}
            )
            
            # Try to geocode for better location data
            if nlp_analyzer:
                geocoded = nlp_analyzer.geocode_location(city)
                if geocoded:
                    self.add_signal(
                        geocoded.get('city', city),
                        'geocoded_location',
                        metadata={
                            'lat': geocoded.get('latitude'),
                            'lon': geocoded.get('longitude'),
                            'country': geocoded.get('country')
                        }
                    )
        
        # Country mentions (medium-high confidence)
        for country in analysis.get('countries_mentioned', []):
            self.add_signal(
                country,
                'country_mentioned',
                level='country',
                metadata={'comment_id': analysis.get('comment_id')}
            )
        
        # Language-based inference (low confidence)
        language = analysis.get('language')
        if language and language != 'unknown' and nlp_analyzer:
            inferred_country = nlp_analyzer.infer_country_from_language(language)
            if inferred_country:
                self.add_signal(
                    inferred_country,
                    'language_to_country',
                    level='country',
                    metadata={'language': language}
                )
    
    def process_all_analyses(self, analyses_df: pd.DataFrame, nlp_analyzer=None):
        """
        Process all comment analyses
        
        Args:
            analyses_df: DataFrame with comment analyses
            nlp_analyzer: NLPAnalyzer instance
        """
        logger.info("Processing all comment analyses for intelligence aggregation...")
        
        for idx, row in analyses_df.iterrows():
            if idx % 100 == 0:
                logger.info(f"Processed {idx}/{len(analyses_df)} analyses")
            
            self.process_comment_analysis(row.to_dict(), nlp_analyzer)
        
        logger.info("Intelligence aggregation complete")
    
    def get_top_locations(self, n: int = 20, level: str = 'city') -> pd.DataFrame:
        """
        Get top N locations by confidence score
        
        Args:
            n: Number of top locations to return
            level: 'city' or 'country'
            
        Returns:
            DataFrame with ranked locations
        """
        target = self.location_scores if level == 'city' else self.country_scores
        
        locations_data = []
        for location, data in target.items():
            locations_data.append({
                'location': location,
                'total_score': data['score'],
                'mention_count': data['count'],
                'avg_confidence': data['score'] / data['count'] if data['count'] > 0 else 0,
                'signal_types': list(set([s['type'] for s in data['signals']])),
                'num_signals': len(data['signals'])
            })
        
        df = pd.DataFrame(locations_data)
        
        if len(df) == 0:
            return df
        
        df = df.sort_values('total_score', ascending=False).head(n)
        df = df.reset_index(drop=True)
        
        return df
    
    def calculate_confidence_level(self, score: float, count: int) -> str:
        """
        Determine confidence level based on score and count
        
        Args:
            score: Total confidence score
            count: Number of mentions
            
        Returns:
            'High', 'Medium', or 'Low'
        """
        avg_confidence = score / count if count > 0 else 0
        
        if avg_confidence >= 0.7 and count >= 3:
            return 'High'
        elif avg_confidence >= 0.5 or count >= 5:
            return 'Medium'
        else:
            return 'Low'
    
    def estimate_viewer_distribution(self, top_n: int = 20) -> Dict:
        """
        Estimate viewer geographic distribution
        
        Args:
            top_n: Number of top locations to include
            
        Returns:
            Dictionary with distribution estimates
        """
        cities_df = self.get_top_locations(top_n, level='city')
        countries_df = self.get_top_locations(top_n, level='country')
        
        # Normalize scores to percentages
        if len(cities_df) > 0:
            total_city_score = cities_df['total_score'].sum()
            cities_df['estimated_percentage'] = (cities_df['total_score'] / total_city_score * 100).round(2)
            cities_df['confidence_level'] = cities_df.apply(
                lambda row: self.calculate_confidence_level(row['total_score'], row['mention_count']),
                axis=1
            )
        
        if len(countries_df) > 0:
            total_country_score = countries_df['total_score'].sum()
            countries_df['estimated_percentage'] = (countries_df['total_score'] / total_country_score * 100).round(2)
            countries_df['confidence_level'] = countries_df.apply(
                lambda row: self.calculate_confidence_level(row['total_score'], row['mention_count']),
                axis=1
            )
        
        return {
            'cities': cities_df,
            'countries': countries_df,
            'summary': {
                'total_cities_identified': len(self.location_scores),
                'total_countries_identified': len(self.country_scores),
                'top_city': cities_df.iloc[0]['location'] if len(cities_df) > 0 else None,
                'top_country': countries_df.iloc[0]['location'] if len(countries_df) > 0 else None
            }
        }
    
    def get_signal_breakdown(self) -> Dict:
        """Get breakdown of signal types used"""
        signal_counts = defaultdict(int)
        
        for location_data in self.location_scores.values():
            for signal in location_data['signals']:
                signal_counts[signal['type']] += 1
        
        for country_data in self.country_scores.values():
            for signal in country_data['signals']:
                signal_counts[signal['type']] += 1
        
        return dict(signal_counts)
    
    def export_results(self, output_path: str):
        """Export aggregation results to CSV"""
        distribution = self.estimate_viewer_distribution(top_n=50)
        
        # Export cities
        if len(distribution['cities']) > 0:
            cities_path = output_path.replace('.csv', '_cities.csv')
            distribution['cities'].to_csv(cities_path, index=False)
            logger.info(f"Cities exported to: {cities_path}")
        
        # Export countries
        if len(distribution['countries']) > 0:
            countries_path = output_path.replace('.csv', '_countries.csv')
            distribution['countries'].to_csv(countries_path, index=False)
            logger.info(f"Countries exported to: {countries_path}")
        
        return distribution


if __name__ == "__main__":
    # Example usage
    aggregator = IntelligenceAggregator()
    
    # Simulate adding signals
    aggregator.add_signal("New York", "city_mentioned")
    aggregator.add_signal("New York", "city_mentioned")
    aggregator.add_signal("London", "city_mentioned")
    aggregator.add_signal("United States", "country_mentioned", level='country')
    
    distribution = aggregator.estimate_viewer_distribution()
    print(distribution['cities'])
    print(distribution['countries'])
