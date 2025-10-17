"""
YouTube Data Collection Module
Collects video metadata and comments using YouTube Data API v3 and yt-dlp
"""

import os
import json
import time
from typing import Dict, List, Optional
from datetime import datetime
import logging

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import yt_dlp
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class YouTubeDataCollector:
    """Collects YouTube video data using multiple methods"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the data collector
        
        Args:
            api_key: YouTube Data API v3 key (optional, will try to load from .env)
        """
        load_dotenv()
        self.api_key = api_key or os.getenv('YOUTUBE_API_KEY')
        self.youtube = None
        
        if self.api_key and self.api_key != 'your_api_key_here':
            try:
                self.youtube = build('youtube', 'v3', developerKey=self.api_key)
                logger.info("YouTube API initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize YouTube API: {e}")
                self.youtube = None
        else:
            logger.warning("No valid YouTube API key found. API methods will be unavailable.")
    
    def extract_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL"""
        if 'v=' in url:
            return url.split('v=')[1].split('&')[0]
        elif 'youtu.be/' in url:
            return url.split('youtu.be/')[1].split('?')[0]
        else:
            return url
    
    def get_video_metadata_api(self, video_id: str) -> Dict:
        """
        Get video metadata using YouTube Data API
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Dictionary containing video metadata
        """
        if not self.youtube:
            logger.error("YouTube API not initialized")
            return {}
        
        try:
            request = self.youtube.videos().list(
                part='snippet,statistics,contentDetails,topicDetails',
                id=video_id
            )
            response = request.execute()
            
            if not response.get('items'):
                logger.error(f"No video found with ID: {video_id}")
                return {}
            
            video = response['items'][0]
            
            metadata = {
                'video_id': video_id,
                'title': video['snippet']['title'],
                'description': video['snippet']['description'],
                'channel_id': video['snippet']['channelId'],
                'channel_title': video['snippet']['channelTitle'],
                'published_at': video['snippet']['publishedAt'],
                'view_count': int(video['statistics'].get('viewCount', 0)),
                'like_count': int(video['statistics'].get('likeCount', 0)),
                'comment_count': int(video['statistics'].get('commentCount', 0)),
                'duration': video['contentDetails']['duration'],
                'tags': video['snippet'].get('tags', []),
                'category_id': video['snippet'].get('categoryId'),
                'default_language': video['snippet'].get('defaultLanguage'),
                'default_audio_language': video['snippet'].get('defaultAudioLanguage'),
                'collected_at': datetime.now().isoformat(),
                'collection_method': 'youtube_api'
            }
            
            logger.info(f"Collected metadata for video: {metadata['title']}")
            return metadata
            
        except HttpError as e:
            logger.error(f"YouTube API error: {e}")
            return {}
    
    def get_video_metadata_ytdlp(self, video_url: str) -> Dict:
        """
        Get video metadata using yt-dlp (fallback method)
        
        Args:
            video_url: Full YouTube video URL
            
        Returns:
            Dictionary containing video metadata
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                
                metadata = {
                    'video_id': info.get('id'),
                    'title': info.get('title'),
                    'description': info.get('description'),
                    'channel_id': info.get('channel_id'),
                    'channel_title': info.get('uploader'),
                    'published_at': info.get('upload_date'),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'comment_count': info.get('comment_count', 0),
                    'duration': info.get('duration'),
                    'tags': info.get('tags', []),
                    'categories': info.get('categories', []),
                    'collected_at': datetime.now().isoformat(),
                    'collection_method': 'yt-dlp'
                }
                
                logger.info(f"Collected metadata via yt-dlp for: {metadata['title']}")
                return metadata
                
        except Exception as e:
            logger.error(f"yt-dlp error: {e}")
            return {}
    
    def get_comments_api(self, video_id: str, max_comments: int = 1000) -> List[Dict]:
        """
        Get video comments using YouTube Data API
        
        Args:
            video_id: YouTube video ID
            max_comments: Maximum number of comments to retrieve
            
        Returns:
            List of comment dictionaries
        """
        if not self.youtube:
            logger.error("YouTube API not initialized")
            return []
        
        comments = []
        next_page_token = None
        
        try:
            while len(comments) < max_comments:
                request = self.youtube.commentThreads().list(
                    part='snippet,replies',
                    videoId=video_id,
                    maxResults=min(100, max_comments - len(comments)),
                    pageToken=next_page_token,
                    textFormat='plainText',
                    order='relevance'
                )
                
                response = request.execute()
                
                for item in response.get('items', []):
                    top_comment = item['snippet']['topLevelComment']['snippet']
                    
                    comment_data = {
                        'comment_id': item['id'],
                        'author': top_comment['authorDisplayName'],
                        'author_channel_id': top_comment.get('authorChannelId', {}).get('value'),
                        'text': top_comment['textDisplay'],
                        'like_count': top_comment['likeCount'],
                        'published_at': top_comment['publishedAt'],
                        'updated_at': top_comment['updatedAt'],
                        'reply_count': item['snippet']['totalReplyCount'],
                        'is_reply': False
                    }
                    comments.append(comment_data)
                    
                    # Get replies if they exist
                    if item['snippet']['totalReplyCount'] > 0 and 'replies' in item:
                        for reply in item['replies']['comments']:
                            reply_snippet = reply['snippet']
                            reply_data = {
                                'comment_id': reply['id'],
                                'author': reply_snippet['authorDisplayName'],
                                'author_channel_id': reply_snippet.get('authorChannelId', {}).get('value'),
                                'text': reply_snippet['textDisplay'],
                                'like_count': reply_snippet['likeCount'],
                                'published_at': reply_snippet['publishedAt'],
                                'updated_at': reply_snippet['updatedAt'],
                                'reply_count': 0,
                                'is_reply': True,
                                'parent_id': item['id']
                            }
                            comments.append(reply_data)
                
                next_page_token = response.get('nextPageToken')
                
                if not next_page_token:
                    break
                
                # Rate limiting
                time.sleep(0.5)
                
                logger.info(f"Collected {len(comments)} comments so far...")
            
            logger.info(f"Total comments collected: {len(comments)}")
            return comments
            
        except HttpError as e:
            logger.error(f"YouTube API error while fetching comments: {e}")
            return comments
    
    def collect_all_data(self, video_url: str, max_comments: int = 1000) -> Dict:
        """
        Collect all available data for a video
        
        Args:
            video_url: YouTube video URL
            max_comments: Maximum number of comments to collect
            
        Returns:
            Dictionary containing all collected data
        """
        video_id = self.extract_video_id(video_url)
        logger.info(f"Starting data collection for video ID: {video_id}")
        
        # Try API first, fallback to yt-dlp
        metadata = self.get_video_metadata_api(video_id)
        if not metadata:
            logger.info("Falling back to yt-dlp for metadata...")
            metadata = self.get_video_metadata_ytdlp(video_url)
        
        # Collect comments (API only for now)
        comments = []
        if self.youtube:
            comments = self.get_comments_api(video_id, max_comments)
        else:
            logger.warning("Cannot collect comments without YouTube API key")
        
        data = {
            'metadata': metadata,
            'comments': comments,
            'collection_summary': {
                'video_id': video_id,
                'video_url': video_url,
                'total_comments': len(comments),
                'collection_timestamp': datetime.now().isoformat(),
                'api_available': self.youtube is not None
            }
        }
        
        return data
    
    def save_data(self, data: Dict, output_path: str):
        """Save collected data to JSON file"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Data saved to: {output_path}")


if __name__ == "__main__":
    # Example usage
    collector = YouTubeDataCollector()
    video_url = "https://www.youtube.com/watch?v=ggJg6CcKtZE"
    
    data = collector.collect_all_data(video_url, max_comments=1000)
    collector.save_data(data, "../data/raw/video_data.json")
