"""
Data Processing Module
Cleans and transforms raw Reddit data for ML pipeline
"""

import pandas as pd
import re
from pathlib import Path
import sys
import json
from pymongo import MongoClient

sys.path.append(str(Path(__file__).parent.parent.parent))
from config import MONGO_CONFIG, logger

class DataProcessor:
    """Process and clean Reddit data"""
    
    def __init__(self):
        self.mongo_client = None
        self.db = None
        
    def connect_mongodb(self):
        """Connect to MongoDB"""
        try:
            self.mongo_client = MongoClient(
                MONGO_CONFIG['uri'],
                serverSelectionTimeoutMS=MONGO_CONFIG['timeout']
            )
            self.mongo_client.server_info()
            self.db = self.mongo_client[MONGO_CONFIG['db_name']]
            logger.success("✓ Connected to MongoDB")
            return True
        except Exception as e:
            logger.warning(f"MongoDB not available: {e}")
            return False
    
    def load_from_mongodb(self):
        """Load raw data from MongoDB"""
        try:
            collection = self.db[MONGO_CONFIG['collections']['reddit_raw']]
            data = list(collection.find())
            logger.info(f"Loaded {len(data)} documents from MongoDB")
            return pd.DataFrame(data)
        except Exception as e:
            logger.error(f"Error loading from MongoDB: {e}")
            return None
    
    def load_from_json(self):
        """Fallback: Load from local JSON files"""
        try:
            json_dir = Path('data/raw_json')
            if not json_dir.exists():
                logger.error("No raw JSON data found")
                return None
            
            all_posts = []
            for json_file in json_dir.glob('*.json'):
                with open(json_file, 'r', encoding='utf-8') as f:
                    posts = json.load(f)
                    all_posts.extend(posts if isinstance(posts, list) else [posts])
            
            logger.info(f"Loaded {len(all_posts)} posts from JSON files")
            return pd.DataFrame(all_posts)
            
        except Exception as e:
            logger.error(f"Error loading from JSON: {e}")
            return None
    
    def clean_text(self, text):
        """Clean and normalize text data"""
        if not isinstance(text, str):
            return ""
        
        # Remove URLs
        text = re.sub(r'http\S+|www.\S+', '', text)
        
        # Remove Reddit markdown
        text = re.sub(r'\[.*?\]\(.*?\)', '', text)
        
        # Remove special characters (keep basic punctuation)
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Lowercase
        text = text.lower()
        
        return text
    
    def extract_temporal_features(self, df):
        """Extract time-based features"""
        try:
            df['created_utc'] = pd.to_datetime(df['created_utc'])
            df['hour'] = df['created_utc'].dt.hour
            df['day_of_week'] = df['created_utc'].dt.dayofweek
            df['day_name'] = df['created_utc'].dt.day_name()
            df['month'] = df['created_utc'].dt.month
            logger.info("✓ Extracted temporal features")
        except Exception as e:
            logger.warning(f"Could not extract temporal features: {e}")
        
        return df
    
    def calculate_engagement_metrics(self, df):
        """Calculate engagement-related metrics"""
        try:
            # Comments per score ratio
            df['comment_ratio'] = df['num_comments'] / (df['score'] + 1)
            
            # Engagement score (weighted)
            df['engagement_score'] = (df['score'] * 0.7) + (df['num_comments'] * 0.3)
            
            # Text length features
            df['title_length'] = df['title'].str.len()
            df['body_length'] = df['body'].str.len()
            df['total_text_length'] = df['title_length'] + df['body_length']
            
            logger.info("✓ Calculated engagement metrics")
        except Exception as e:
            logger.warning(f"Could not calculate engagement metrics: {e}")
        
        return df
    
    def process_comments(self, df):
        """Process comments data"""
        try:
            # Extract comment count
            df['num_comments_extracted'] = df['comments'].apply(
                lambda x: len(x) if isinstance(x, list) else 0
            )
            
            # Combine all comment text
            df['all_comments_text'] = df['comments'].apply(
                lambda x: ' '.join([c.get('body', '') for c in x]) if isinstance(x, list) else ''
            )
            
            logger.info("✓ Processed comments data")
        except Exception as e:
            logger.warning(f"Could not process comments: {e}")
        
        return df
    
    def process(self):
        """Main processing workflow"""
        logger.info("Starting data processing...")
        
        # Load data
        mongo_ok = self.connect_mongodb()
        
        if mongo_ok:
            df = self.load_from_mongodb()
        else:
            df = self.load_from_json()
        
        if df is None or len(df) == 0:
            logger.error("No data to process")
            return None
        
        logger.info(f"Processing {len(df)} posts...")
        
        # Handle missing values
        df['body'] = df['body'].fillna('')
        df['title'] = df['title'].fillna('')
        
        # Clean text fields
        logger.info("Cleaning text data...")
        df['title_clean'] = df['title'].apply(self.clean_text)
        df['body_clean'] = df['body'].apply(self.clean_text)
        
        # Combine title and body for analysis
        df['full_text'] = df['title_clean'] + ' ' + df['body_clean']
        
        # Extract features
        df = self.extract_temporal_features(df)
        df = self.calculate_engagement_metrics(df)
        df = self.process_comments(df)
        
        # Remove duplicates
        initial_count = len(df)
        df = df.drop_duplicates(subset=['post_id'], keep='first')
        logger.info(f"Removed {initial_count - len(df)} duplicate posts")
        
        # Save processed data
        output_path = Path('data/processed_reddit_data.csv')
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        
        logger.success(f"✅ Processing complete! Saved {len(df)} processed posts to {output_path}")
        
        # Display summary statistics
        logger.info("\n📊 Data Summary:")
        logger.info(f"  Total posts: {len(df)}")
        logger.info(f"  Subreddits: {df['subreddit'].nunique()}")
        logger.info(f"  Date range: {df['created_utc'].min()} to {df['created_utc'].max()}")
        logger.info(f"  Avg score: {df['score'].mean():.2f}")
        logger.info(f"  Avg comments: {df['num_comments'].mean():.2f}")
        
        return df
    
    def close(self):
        """Close connections"""
        if self.mongo_client:
            self.mongo_client.close()

def main():
    """Main execution"""
    processor = DataProcessor()
    
    try:
        processor.process()
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise
    finally:
        processor.close()

if __name__ == "__main__":
    main()