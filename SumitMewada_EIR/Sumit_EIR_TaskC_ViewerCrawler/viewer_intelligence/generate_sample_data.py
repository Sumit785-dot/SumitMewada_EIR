"""
Sample Data Generator
Creates sample cached data for testing without API access
"""

import json
import os
from datetime import datetime, timedelta
import random


def generate_sample_comments(n=100):
    """Generate sample comments with geographic mentions"""
    
    cities = [
        "New York", "London", "Tokyo", "Paris", "Mumbai", "Sydney", "Toronto",
        "Berlin", "Singapore", "Dubai", "Los Angeles", "Chicago", "Boston",
        "San Francisco", "Seattle", "Austin", "Miami", "Atlanta", "Houston",
        "Mexico City", "São Paulo", "Buenos Aires", "Madrid", "Barcelona",
        "Rome", "Amsterdam", "Stockholm", "Copenhagen", "Oslo", "Helsinki"
    ]
    
    countries = [
        "United States", "United Kingdom", "Japan", "France", "India",
        "Australia", "Canada", "Germany", "Singapore", "UAE", "Mexico",
        "Brazil", "Argentina", "Spain", "Italy", "Netherlands", "Sweden",
        "Denmark", "Norway", "Finland"
    ]
    
    comment_templates = [
        "Greetings from {city}! This is amazing!",
        "Watching this from {city}, love it!",
        "Hello from {country}! Great video!",
        "I'm in {city} and this is so cool!",
        "{city} viewer here! Awesome content!",
        "Love this! From {country}",
        "This is great! Greetings from {city}",
        "Watching from {city}, {country}. Fantastic!",
        "Amazing video! Love from {city}",
        "Great work! Viewer from {country}",
        "This is awesome!",  # No location
        "Love it!",  # No location
        "Incredible content!",  # No location
    ]
    
    languages = ['en', 'es', 'fr', 'de', 'ja', 'pt', 'it', 'nl', 'sv', 'no']
    
    comments = []
    base_time = datetime.now() - timedelta(days=30)
    
    for i in range(n):
        template = random.choice(comment_templates)
        
        # Generate comment text
        if '{city}' in template and '{country}' in template:
            city = random.choice(cities)
            country = random.choice(countries)
            text = template.format(city=city, country=country)
        elif '{city}' in template:
            city = random.choice(cities)
            text = template.format(city=city)
        elif '{country}' in template:
            country = random.choice(countries)
            text = template.format(country=country)
        else:
            text = template
        
        # Add random timestamp
        timestamp = base_time + timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        comment = {
            'comment_id': f'comment_{i:04d}',
            'author': f'User{i:04d}',
            'author_channel_id': f'channel_{i:04d}',
            'text': text,
            'like_count': random.randint(0, 100),
            'published_at': timestamp.isoformat() + 'Z',
            'updated_at': timestamp.isoformat() + 'Z',
            'reply_count': random.randint(0, 5),
            'is_reply': False
        }
        
        comments.append(comment)
    
    return comments


def generate_sample_data(video_id='ggJg6CcKtZE', num_comments=500):
    """Generate complete sample dataset"""
    
    metadata = {
        'video_id': video_id,
        'title': 'Sample Video Title - Geographic Distribution Test',
        'description': 'This is a sample video for testing the viewer intelligence crawler.',
        'channel_id': 'UC_sample_channel_id',
        'channel_title': 'Sample Channel',
        'published_at': '2024-01-01T12:00:00Z',
        'view_count': 1500000,
        'like_count': 45000,
        'comment_count': num_comments,
        'duration': 'PT10M30S',
        'tags': ['sample', 'test', 'geography', 'international'],
        'category_id': '22',
        'default_language': 'en',
        'default_audio_language': 'en',
        'collected_at': datetime.now().isoformat(),
        'collection_method': 'sample_generator'
    }
    
    comments = generate_sample_comments(num_comments)
    
    data = {
        'metadata': metadata,
        'comments': comments,
        'collection_summary': {
            'video_id': video_id,
            'video_url': f'https://www.youtube.com/watch?v={video_id}',
            'total_comments': len(comments),
            'collection_timestamp': datetime.now().isoformat(),
            'api_available': False,
            'note': 'This is sample data generated for testing purposes'
        }
    }
    
    return data


def main():
    """Generate and save sample data"""
    print("Generating sample data...")
    
    # Generate data
    data = generate_sample_data(num_comments=500)
    
    # Create directory
    os.makedirs('data/cache', exist_ok=True)
    
    # Save to cache
    output_path = 'data/cache/video_data.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"[OK] Sample data generated: {output_path}")
    print(f"  - Video ID: {data['metadata']['video_id']}")
    print(f"  - Comments: {len(data['comments'])}")
    print(f"  - Title: {data['metadata']['title']}")
    print("\nYou can now run the pipeline with USE_CACHE=True")


if __name__ == "__main__":
    main()
