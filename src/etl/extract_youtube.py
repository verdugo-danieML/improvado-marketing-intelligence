"""
YouTube Comments Extractor for Marketing Intelligence
Extracts comments from videos mentioning brands like ASUS, Activision, etc.
"""

import os
import json
from datetime import datetime
from pathlib import Path
import time
import sys
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Load environment variables
load_dotenv()

class YouTubeExtractor:
    """Extract comments from YouTube videos about specific brands"""
    
    def __init__(self):
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        if not self.api_key:
            raise ValueError("YOUTUBE_API_KEY not found in .env file")
        
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        self.comments = []
        
        # Target brands (Improvado clients)
        self.brands = [
            'ASUS',
            'Activision',
        ]
    
    def search_brand_videos(self, brand, max_results=10):
        """Search for videos mentioning a brand"""
        try:
            print(f"\n🔍 Searching videos for: {brand}")
            
            # Search for brand reviews, unboxings, discussions
            search_queries = [
                f"{brand} review",
                f"{brand} unboxing",
                f"{brand} gaming",
                f"{brand} product"
            ]
            
            video_ids = []
            
            for query in search_queries[:2]:  # Limit to 2 queries per brand to save quota
                request = self.youtube.search().list(
                    part='id,snippet',
                    q=query,
                    type='video',
                    maxResults=max_results // 2,
                    order='relevance',
                    relevanceLanguage='en',
                    safeSearch='moderate'
                )
                
                response = request.execute()
                
                for item in response.get('items', []):
                    if item['id']['kind'] == 'youtube#video':
                        video_ids.append({
                            'video_id': item['id']['videoId'],
                            'title': item['snippet']['title'],
                            'channel': item['snippet']['channelTitle'],
                            'published_at': item['snippet']['publishedAt'],
                            'brand': brand,
                            'search_query': query
                        })
                
                print(f"  Found {len(response.get('items', []))} videos for '{query}'")
                time.sleep(0.5)  # Rate limiting courtesy
            
            print(f"✅ Total videos found for {brand}: {len(video_ids)}")
            return video_ids
            
        except HttpError as e:
            print(f"❌ Error searching videos: {e}")
            return []
    
    def extract_video_comments(self, video_id, video_info, max_comments=100):
        """Extract comments from a specific video"""
        try:
            comments = []
            next_page_token = None
            
            while len(comments) < max_comments:
                request = self.youtube.commentThreads().list(
                    part='snippet',
                    videoId=video_id,
                    maxResults=min(100, max_comments - len(comments)),
                    pageToken=next_page_token,
                    textFormat='plainText',
                    order='relevance'
                )
                
                response = request.execute()
                
                for item in response.get('items', []):
                    comment_snippet = item['snippet']['topLevelComment']['snippet']
                    
                    comment = {
                        'id': item['id'],
                        'video_id': video_id,
                        'video_title': video_info['title'],
                        'video_channel': video_info['channel'],
                        'brand': video_info['brand'],
                        'text': comment_snippet['textDisplay'],
                        'author': comment_snippet['authorDisplayName'],
                        'like_count': comment_snippet['likeCount'],
                        'published_at': comment_snippet['publishedAt'],
                        'updated_at': comment_snippet.get('updatedAt', comment_snippet['publishedAt']),
                        'reply_count': item['snippet']['totalReplyCount'],
                        'search_query': video_info['search_query'],
                        'source': 'youtube',
                        'collected_at': datetime.now().isoformat()
                    }
                    
                    comments.append(comment)
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
                
                time.sleep(0.3)  # Rate limiting
            
            return comments
            
        except HttpError as e:
            if e.resp.status == 403:
                print(f"  ⚠️  Comments disabled for video: {video_info['title'][:50]}...")
            else:
                print(f"  ❌ Error extracting comments: {e}")
            return []
    
    def extract_all_comments(self, videos_per_brand=5, comments_per_video=50):
        """Extract comments for all brands"""
        all_comments = []
        total_quota_used = 0
        
        print("="*70)
        print("🎬 YOUTUBE COMMENTS EXTRACTION")
        print("="*70)
        print(f"\nTarget brands: {', '.join(self.brands)}")
        print(f"Videos per brand: {videos_per_brand}")
        print(f"Comments per video: {comments_per_video}")
        print(f"Expected total comments: ~{len(self.brands) * videos_per_brand * comments_per_video}")
        
        for brand in self.brands:
            print(f"\n{'='*70}")
            print(f"Processing brand: {brand}")
            print(f"{'='*70}")
            
            # Search videos
            videos = self.search_brand_videos(brand, max_results=videos_per_brand)
            total_quota_used += 100  # Each search costs ~100 quota units
            
            if not videos:
                print(f"⚠️  No videos found for {brand}")
                continue
            
            # Extract comments from each video
            for idx, video_info in enumerate(videos, 1):
                print(f"\n  Video {idx}/{len(videos)}: {video_info['title'][:60]}...")
                
                comments = self.extract_video_comments(
                    video_info['video_id'],
                    video_info,
                    max_comments=comments_per_video
                )
                
                total_quota_used += 1  # Each commentThreads.list costs 1 unit
                
                if comments:
                    all_comments.extend(comments)
                    print(f"    ✅ Extracted {len(comments)} comments")
                else:
                    print("    ⚠️  No comments available")
                
                time.sleep(0.5)  # Be nice to the API
        
        self.comments = all_comments
        
        print("\n" + "="*70)
        print("EXTRACTION SUMMARY")
        print("="*70)
        print(f"Total comments collected: {len(all_comments)}")
        print(f"Estimated quota used: {total_quota_used} / 10,000 daily limit")
        print(f"Remaining quota: ~{10000 - total_quota_used}")
        
        return all_comments
    
    def save_to_json(self, filename='data/youtube_comments.json'):
        """Save comments to JSON file"""
        output_path = Path(__file__).parent.parent.parent / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.comments, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Saved {len(self.comments)} comments to {output_path}")
        return output_path
    
    
    def generate_statistics(self):
        """Print collection statistics"""
        if not self.comments:
            print("No comments to analyze")
            return
        
        print("\n" + "="*70)
        print("DATASET STATISTICS")
        print("="*70)
        
        # By brand
        print("\nComments by Brand:")
        brands = {}
        for comment in self.comments:
            brand = comment['brand']
            brands[brand] = brands.get(brand, 0) + 1
        
        for brand, count in sorted(brands.items(), key=lambda x: x[1], reverse=True):
            print(f"  {brand}: {count}")
        
        # Engagement stats
        avg_likes = sum(c['like_count'] for c in self.comments) / len(self.comments)
        total_replies = sum(c['reply_count'] for c in self.comments)
        
        print("\nEngagement Metrics:")
        print(f"  Average likes per comment: {avg_likes:.1f}")
        print(f"  Total replies: {total_replies}")
        
        # Top videos
        print("\nTop 5 Videos by Comment Count:")
        video_counts = {}
        for comment in self.comments:
            video_id = comment['video_id']
            video_title = comment['video_title']
            key = f"{video_title[:50]}..."
            video_counts[key] = video_counts.get(key, 0) + 1
        
        for idx, (video, count) in enumerate(sorted(video_counts.items(), key=lambda x: x[1], reverse=True)[:5], 1):
            print(f"  {idx}. {video}: {count} comments")
        
        print("="*70)

def main():
    """Main execution"""
    try:
        # Initialize extractor
        extractor = YouTubeExtractor()
        
        # Extract comments
        # Adjust these parameters based on your needs:
        # - videos_per_brand: How many videos to check per brand (5-10 recommended)
        # - comments_per_video: How many comments per video (50-100 recommended)
        comments = extractor.extract_all_comments(
            videos_per_brand=5,      # 5 videos per brand
            comments_per_video=50    # 50 comments per video
        )
        
        if not comments:
            print("\n❌ No comments extracted. Please check your API key and quota.")
            return
        
        # Save to JSON
        extractor.save_to_json()
        
        # Show statistics
        extractor.generate_statistics()
        
        print("\n✅ YOUTUBE EXTRACTION COMPLETE!")
        print("\nNext steps:")
        print("1. Run: python src/etl/process_youtube_data.py")
        print("2. Run: python src/ml/sentiment_analysis.py")
        print("3. Run: python src/etl/load_to_sqlite.py")
        print("4. Run: streamlit run app.py")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check that YOUTUBE_API_KEY is set in .env file")
        print("2. Verify API key is valid at: https://console.cloud.google.com/")
        print("3. Ensure YouTube Data API v3 is enabled")
        print("4. Check daily quota hasn't been exceeded")

if __name__ == "__main__":
    main()