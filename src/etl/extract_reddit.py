"""
Reddit Data Extraction Module
Extracts posts and comments from marketing-related subreddits
"""

import praw
from pymongo import MongoClient, errors
import json
from datetime import datetime
from pathlib import Path
import sys
import time

sys.path.append(str(Path(__file__).parent.parent.parent))
from config import REDDIT_CONFIG, MONGO_CONFIG, REDDIT_SOURCES, APP_CONFIG, logger

class RedditExtractor:
    """Extract data from Reddit API"""
    
    def __init__(self):
        """Initialize Reddit API client"""
        self.reddit = None
        self.mongo_client = None
        self.db = None
        self.collection = None
        self.posts_collected = 0
        
    def connect_reddit(self):
        """Connect to Reddit API"""
        try:
            if not REDDIT_CONFIG['client_id'] or not REDDIT_CONFIG['client_secret']:
                logger.warning("Reddit credentials not configured - running in demo mode")
                return False
            
            self.reddit = praw.Reddit(
                client_id=REDDIT_CONFIG['client_id'],
                client_secret=REDDIT_CONFIG['client_secret'],
                user_agent=REDDIT_CONFIG['user_agent']
            )
            
            # Test connection
            self.reddit.user.me()
            logger.success("✓ Connected to Reddit API")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Reddit: {e}")
            return False
    
    def connect_mongodb(self):
        """Connect to MongoDB"""
        try:
            self.mongo_client = MongoClient(
                MONGO_CONFIG['uri'],
                serverSelectionTimeoutMS=MONGO_CONFIG['timeout']
            )
            
            # Test connection
            self.mongo_client.server_info()
            
            self.db = self.mongo_client[MONGO_CONFIG['db_name']]
            self.collection = self.db[MONGO_CONFIG['collections']['reddit_raw']]
            
            logger.success("✓ Connected to MongoDB")
            return True
            
        except errors.ServerSelectionTimeoutError:
            logger.warning("MongoDB not available - will save to local JSON")
            return False
        except Exception as e:
            logger.error(f"MongoDB connection error: {e}")
            return False
    
    def extract_post_data(self, post):
        """Extract relevant data from a Reddit post"""
        try:
            return {
                'post_id': post.id,
                'subreddit': str(post.subreddit),
                'title': post.title,
                'body': post.selftext if hasattr(post, 'selftext') else '',
                'author': str(post.author) if post.author else '[deleted]',
                'score': post.score,
                'upvote_ratio': post.upvote_ratio,
                'num_comments': post.num_comments,
                'created_utc': datetime.fromtimestamp(post.created_utc).isoformat(),
                'url': post.url,
                'permalink': f"https://reddit.com{post.permalink}",
                'is_self': post.is_self,
                'extracted_at': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error extracting post data: {e}")
            return None
    
    def extract_comments(self, post, limit=5):
        """Extract top comments from a post"""
        comments = []
        try:
            post.comments.replace_more(limit=0)  # Remove "More Comments" objects
            for comment in post.comments.list()[:limit]:
                if hasattr(comment, 'body'):
                    comments.append({
                        'comment_id': comment.id,
                        'author': str(comment.author) if comment.author else '[deleted]',
                        'body': comment.body,
                        'score': comment.score,
                        'created_utc': datetime.fromtimestamp(comment.created_utc).isoformat()
                    })
        except Exception as e:
            logger.error(f"Error extracting comments: {e}")
        
        return comments
    
    def search_subreddit(self, subreddit_name, search_term, limit=20):
        """Search for posts in a subreddit"""
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            posts = []
            
            for post in subreddit.search(search_term, limit=limit, time_filter='month'):
                post_data = self.extract_post_data(post)
                if post_data:
                    post_data['search_term'] = search_term
                    post_data['comments'] = self.extract_comments(post)
                    posts.append(post_data)
                    self.posts_collected += 1
                
                # Rate limiting
                time.sleep(0.5)
            
            return posts
            
        except Exception as e:
            logger.error(f"Error searching r/{subreddit_name} for '{search_term}': {e}")
            return []
    
    def save_to_mongodb(self, posts):
        """Save posts to MongoDB"""
        if not self.collection:
            return False
        
        try:
            if posts:
                result = self.collection.insert_many(posts)
                logger.info(f"  → Saved {len(result.inserted_ids)} posts to MongoDB")
                return True
        except Exception as e:
            logger.error(f"Error saving to MongoDB: {e}")
            return False
    
    def save_to_json(self, posts, filename):
        """Fallback: Save posts to local JSON file"""
        try:
            output_dir = Path('data/raw_json')
            output_dir.mkdir(parents=True, exist_ok=True)
            
            filepath = output_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(posts, f, indent=2, ensure_ascii=False)
            
            logger.info(f"  → Saved {len(posts)} posts to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving to JSON: {e}")
            return False
    
    def extract_all(self):
        """Main extraction workflow"""
        logger.info("Starting Reddit data extraction...")
        
        # Connect to services
        reddit_ok = self.connect_reddit()
        mongo_ok = self.connect_mongodb()
        
        if not reddit_ok:
            logger.error("Cannot proceed without Reddit API access")
            return False
        
        max_posts = APP_CONFIG['max_reddit_posts']
        all_posts = []
        
        # Extract from each subreddit and search term
        for subreddit in REDDIT_SOURCES['subreddits']:
            for search_term in REDDIT_SOURCES['search_terms']:
                if self.posts_collected >= max_posts:
                    logger.info(f"Reached maximum posts limit ({max_posts})")
                    break
                
                logger.info(f"Searching r/{subreddit} for '{search_term}'...")
                posts = self.search_subreddit(subreddit, search_term, limit=10)
                
                if posts:
                    all_posts.extend(posts)
                    
                    # Save incrementally
                    if mongo_ok:
                        self.save_to_mongodb(posts)
                    else:
                        filename = f"{subreddit}_{search_term.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.json"
                        self.save_to_json(posts, filename)
                
                time.sleep(1)  # Rate limiting between searches
            
            if self.posts_collected >= max_posts:
                break
        
        # Save metadata
        metadata = {
            'extraction_date': datetime.now().isoformat(),
            'total_posts': self.posts_collected,
            'subreddits': REDDIT_SOURCES['subreddits'],
            'search_terms': REDDIT_SOURCES['search_terms']
        }
        
        if mongo_ok:
            metadata_coll = self.db[MONGO_CONFIG['collections']['metadata']]
            metadata_coll.insert_one(metadata)
        
        logger.success(f"✅ Extraction complete! Collected {self.posts_collected} posts")
        return True
    
    def close(self):
        """Close connections"""
        if self.mongo_client:
            self.mongo_client.close()

def main():
    """Main execution"""
    extractor = RedditExtractor()
    
    try:
        extractor.extract_all()
    except KeyboardInterrupt:
        logger.warning("Extraction interrupted by user")
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
    finally:
        extractor.close()

if __name__ == "__main__":
    main()