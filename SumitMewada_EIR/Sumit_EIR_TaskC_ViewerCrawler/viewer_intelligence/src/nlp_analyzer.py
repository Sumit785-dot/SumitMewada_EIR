"""
NLP Analysis Module
Performs language detection, NER, and geographic entity extraction
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from collections import Counter, defaultdict

import pandas as pd
from langdetect import detect, LangDetectException
from geotext import GeoText
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import pycountry
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    import spacy
    SPACY_AVAILABLE = True
except Exception as e:
    SPACY_AVAILABLE = False
    logger.warning(f"spaCy not available: {e}")


class NLPAnalyzer:
    """Analyzes text data for language, location, and demographic signals"""
    
    def __init__(self, spacy_model: str = 'en_core_web_sm'):
        """
        Initialize NLP analyzer
        
        Args:
            spacy_model: spaCy model to use (default: en_core_web_sm)
        """
        self.geolocator = Nominatim(user_agent="youtube_viewer_intelligence")
        self.geocode_cache = {}
        
        # Try to load spaCy model
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load(spacy_model)
                logger.info(f"Loaded spaCy model: {spacy_model}")
            except OSError:
                logger.warning(f"spaCy model '{spacy_model}' not found. NER will be limited.")
                logger.info("Install with: python -m spacy download en_core_web_sm")
                self.nlp = None
        else:
            logger.warning("spaCy not available. NER will be limited.")
            self.nlp = None
    
    def detect_language(self, text: str) -> Tuple[str, float]:
        """
        Detect language of text
        
        Args:
            text: Input text
            
        Returns:
            Tuple of (language_code, confidence)
        """
        if not text or len(text.strip()) < 3:
            return ('unknown', 0.0)
        
        try:
            lang = detect(text)
            # langdetect doesn't provide confidence, so we use a heuristic
            confidence = 0.7 if len(text) > 50 else 0.5
            return (lang, confidence)
        except LangDetectException:
            return ('unknown', 0.0)
    
    def extract_locations_geotext(self, text: str) -> Dict[str, List[str]]:
        """
        Extract location mentions using geotext
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with cities and countries
        """
        places = GeoText(text)
        
        return {
            'cities': list(set(places.cities)),
            'countries': list(set(places.countries))
        }
    
    def extract_locations_spacy(self, text: str) -> List[Dict]:
        """
        Extract location entities using spaCy NER
        
        Args:
            text: Input text
            
        Returns:
            List of location entities with metadata
        """
        if not self.nlp:
            return []
        
        doc = self.nlp(text)
        locations = []
        
        for ent in doc.ents:
            if ent.label_ in ['GPE', 'LOC', 'FAC']:  # Geopolitical entity, Location, Facility
                locations.append({
                    'text': ent.text,
                    'label': ent.label_,
                    'start': ent.start_char,
                    'end': ent.end_char
                })
        
        return locations
    
    def geocode_location(self, location_name: str, retry: int = 3) -> Optional[Dict]:
        """
        Geocode a location name to coordinates
        
        Args:
            location_name: Name of the location
            retry: Number of retries
            
        Returns:
            Dictionary with geocoding results or None
        """
        # Check cache first
        if location_name in self.geocode_cache:
            return self.geocode_cache[location_name]
        
        for attempt in range(retry):
            try:
                location = self.geolocator.geocode(location_name, timeout=10)
                
                if location:
                    result = {
                        'name': location_name,
                        'formatted_address': location.address,
                        'latitude': location.latitude,
                        'longitude': location.longitude,
                        'raw': location.raw
                    }
                    
                    # Extract city, country from address
                    address_parts = location.address.split(', ')
                    result['city'] = address_parts[0] if len(address_parts) > 0 else None
                    result['country'] = address_parts[-1] if len(address_parts) > 0 else None
                    
                    self.geocode_cache[location_name] = result
                    return result
                else:
                    self.geocode_cache[location_name] = None
                    return None
                    
            except (GeocoderTimedOut, GeocoderServiceError) as e:
                if attempt < retry - 1:
                    time.sleep(1)
                    continue
                else:
                    logger.warning(f"Geocoding failed for '{location_name}': {e}")
                    return None
        
        return None
    
    def extract_timezone_hints(self, timestamp: str) -> Optional[str]:
        """
        Extract timezone hints from timestamp
        
        Args:
            timestamp: ISO format timestamp
            
        Returns:
            Timezone string or None
        """
        # This is a simplified version - could be enhanced with pytz
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            hour = dt.hour
            
            # Simple heuristic based on posting time
            if 0 <= hour < 6:
                return 'late_night'
            elif 6 <= hour < 12:
                return 'morning'
            elif 12 <= hour < 18:
                return 'afternoon'
            else:
                return 'evening'
        except:
            return None
    
    def analyze_comment(self, comment: Dict) -> Dict:
        """
        Perform comprehensive analysis on a single comment
        
        Args:
            comment: Comment dictionary
            
        Returns:
            Analysis results
        """
        text = comment.get('text', '')
        
        # Language detection
        language, lang_confidence = self.detect_language(text)
        
        # Location extraction
        geotext_locations = self.extract_locations_geotext(text)
        spacy_locations = self.extract_locations_spacy(text)
        
        # Timezone hints
        timezone_hint = self.extract_timezone_hints(comment.get('published_at', ''))
        
        analysis = {
            'comment_id': comment.get('comment_id'),
            'author': comment.get('author'),
            'language': language,
            'language_confidence': lang_confidence,
            'cities_mentioned': geotext_locations['cities'],
            'countries_mentioned': geotext_locations['countries'],
            'spacy_locations': spacy_locations,
            'timezone_hint': timezone_hint,
            'text_length': len(text),
            'published_at': comment.get('published_at')
        }
        
        return analysis
    
    def analyze_all_comments(self, comments: List[Dict]) -> pd.DataFrame:
        """
        Analyze all comments and return results as DataFrame
        
        Args:
            comments: List of comment dictionaries
            
        Returns:
            DataFrame with analysis results
        """
        logger.info(f"Analyzing {len(comments)} comments...")
        
        analyses = []
        for i, comment in enumerate(comments):
            if i % 100 == 0:
                logger.info(f"Processed {i}/{len(comments)} comments")
            
            analysis = self.analyze_comment(comment)
            analyses.append(analysis)
        
        df = pd.DataFrame(analyses)
        logger.info("Comment analysis complete")
        
        return df
    
    def get_language_distribution(self, analyses_df: pd.DataFrame) -> Dict:
        """Get language distribution from analyses"""
        lang_counts = analyses_df['language'].value_counts()
        total = len(analyses_df)
        
        distribution = {}
        for lang, count in lang_counts.items():
            try:
                lang_obj = pycountry.languages.get(alpha_2=lang)
                lang_name = lang_obj.name if lang_obj else lang
            except:
                lang_name = lang
            
            distribution[lang_name] = {
                'count': int(count),
                'percentage': round(count / total * 100, 2),
                'code': lang
            }
        
        return distribution
    
    def get_location_mentions(self, analyses_df: pd.DataFrame) -> Dict:
        """Get aggregated location mentions"""
        all_cities = []
        all_countries = []
        
        for cities in analyses_df['cities_mentioned']:
            all_cities.extend(cities)
        
        for countries in analyses_df['countries_mentioned']:
            all_countries.extend(countries)
        
        city_counts = Counter(all_cities)
        country_counts = Counter(all_countries)
        
        return {
            'cities': dict(city_counts.most_common(50)),
            'countries': dict(country_counts.most_common(50))
        }
    
    def infer_country_from_language(self, language: str) -> Optional[str]:
        """
        Infer likely country from language code
        
        Args:
            language: Language code (e.g., 'en', 'es', 'fr')
            
        Returns:
            Most likely country name or None
        """
        # Mapping of languages to most likely countries
        lang_to_country = {
            'en': 'United States',
            'es': 'Spain',
            'fr': 'France',
            'de': 'Germany',
            'it': 'Italy',
            'pt': 'Brazil',
            'ru': 'Russia',
            'ja': 'Japan',
            'ko': 'South Korea',
            'zh-cn': 'China',
            'zh-tw': 'Taiwan',
            'ar': 'Saudi Arabia',
            'hi': 'India',
            'bn': 'Bangladesh',
            'tr': 'Turkey',
            'vi': 'Vietnam',
            'th': 'Thailand',
            'pl': 'Poland',
            'nl': 'Netherlands',
            'sv': 'Sweden',
            'no': 'Norway',
            'da': 'Denmark',
            'fi': 'Finland',
            'el': 'Greece',
            'cs': 'Czech Republic',
            'hu': 'Hungary',
            'ro': 'Romania',
            'id': 'Indonesia',
            'ms': 'Malaysia',
            'tl': 'Philippines',
            'uk': 'Ukraine',
            'he': 'Israel',
            'fa': 'Iran'
        }
        
        return lang_to_country.get(language)


if __name__ == "__main__":
    # Example usage
    analyzer = NLPAnalyzer()
    
    sample_comment = {
        'comment_id': '123',
        'author': 'TestUser',
        'text': 'Greetings from New York! This video is amazing. Love from NYC!',
        'published_at': '2024-01-15T14:30:00Z'
    }
    
    result = analyzer.analyze_comment(sample_comment)
    print(result)
