"""
Load to SQLite Module
Loads processed and ML-enriched data to SQLite database
"""

import pandas as pd
import sqlite3
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))
from config import SQLITE_CONFIG, logger

class SQLiteLoader:
    """Load data to SQLite database"""
    
    def __init__(self):
        self.conn = None
        self.db_path = SQLITE_CONFIG['db_path']
        
    def connect(self):
        """Connect to SQLite database"""
        try:
            # Ensure directory exists
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            
            self.conn = sqlite3.connect(self.db_path)
            logger.success(f"✓ Connected to SQLite: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to SQLite: {e}")
            return False
    
    def create_schema(self):
        """Create database schema for Reddit data"""
        cursor = self.conn.cursor()
        
        # Create youtube_processed table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS youtube_processed (
                id TEXT PRIMARY KEY,
                video_id TEXT,
                video_title TEXT,
                video_channel TEXT,
                brand TEXT,
                text TEXT,
                author TEXT,
                timestamp DATETIME,
                score INTEGER,
                num_comments INTEGER,
                sentiment_label TEXT,
                sentiment_score REAL,
                engagement_score REAL,
                source TEXT,
                url TEXT,
                extracted_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        
        self.conn.commit()
        logger.info("✓ Database schema created")
    
    def load_processed_data(self, json_path='data/youtube_processed.json'):
        """Load processed data from JSON"""
        try:
            if not Path(json_path).exists():
                logger.error(f"Processed data file not found: {json_path}")
                return None
            
            df = pd.read_json(json_path)
            logger.info(f"Loaded {len(df)} records from {json_path}")
            
            return df
        except Exception as e:
            logger.error(f"Error loading processed data: {e}")
            return None
    
    def load_sentiment_data(self, csv_path='data/youtube_sentiment.csv'):
        """Load sentiment analysis results"""
        try:
            if not Path(csv_path).exists():
                logger.warning(f"Sentiment data not found: {csv_path}")
                return None
            
            df = pd.read_csv(csv_path)
            logger.info(f"Loaded sentiment data for {len(df)} records")
            
            return df
        except Exception as e:
            logger.warning(f"Could not load sentiment data: {e}")
            return None
    
    def merge_data(self, processed_df, sentiment_df):
        """Merge processed data with sentiment results"""
        if sentiment_df is not None:
            # Merge on id
            merged = processed_df.merge(
                sentiment_df[['id', 'sentiment_label', 'sentiment_score']], 
                on='id', 
                how='left'
            )
            logger.info("✓ Merged sentiment data with processed data")
            return merged
        else:
            # Add empty sentiment columns
            processed_df['sentiment_label'] = None
            processed_df['sentiment_score'] = None
            return processed_df
    
    def insert_to_database(self, df):
        """Insert data to SQLite"""
        try:
            # Prepare data for insertion
            df_insert = df.copy()
            
            # Rename columns to match schema
            if 'created_utc' in df_insert.columns:
                df_insert['timestamp'] = df_insert['created_utc']
            
            # Add extracted_date
            df_insert['extracted_date'] = pd.Timestamp.now().date()
            
            # Select only columns that exist in schema
            columns_to_insert = [
                'id', 'video_id', 'video_title', 'video_channel', 'brand',
                'text', 'author', 'timestamp', 'score', 'num_comments',
                'sentiment_label', 'sentiment_score', 'engagement_score',
                'source', 'url', 'extracted_date'
            ]
            
            # Keep only columns that exist in dataframe
            available_columns = [col for col in columns_to_insert if col in df_insert.columns]
            df_final = df_insert[available_columns]
            
            # Insert to database (replace if exists)
            df_final.to_sql('youtube_processed', self.conn, if_exists='replace', index=False)
            
            logger.success(f"✅ Inserted {len(df_final)} records to youtube_processed table")
            
            # Show summary
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM youtube_processed")
            count = cursor.fetchone()[0]
            logger.info(f"  Total records in database: {count}")
            
            # Show sentiment distribution if available
            if 'sentiment_label' in df_final.columns:
                sentiment_counts = df_final['sentiment_label'].value_counts()
                logger.info("  Sentiment distribution:")
                for label, count in sentiment_counts.items():
                    logger.info(f"    {label}: {count}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error inserting data: {e}")
            return False
    
    def verify_data(self):
        """Verify data was loaded correctly"""
        try:
            cursor = self.conn.cursor()
            
            # Check record count
            cursor.execute("SELECT COUNT(*) FROM youtube_processed")
            count = cursor.fetchone()[0]
            
            # Check sample records
            cursor.execute("SELECT id, brand, sentiment_label FROM youtube_processed LIMIT 5")
            samples = cursor.fetchall()
            
            logger.info("\n📊 Data Verification:")
            logger.info(f"  Total records: {count}")
            logger.info("  Sample records:")
            for sample in samples:
                logger.info(f"    {sample}")
            
            return True
            
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return False
    
    def load(self):
        """Main loading workflow"""
        logger.info("Starting data loading to SQLite...")
        
        if not self.connect():
            return False
        
        # Create schema
        self.create_schema()
        
        # Load data
        processed_df = self.load_processed_data()
        if processed_df is None:
            return False
        
        sentiment_df = self.load_sentiment_data()
        
        # Merge data
        final_df = self.merge_data(processed_df, sentiment_df)
        
        # Insert to database
        if self.insert_to_database(final_df):
            self.verify_data()
            return True
        
        return False
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("✓ Database connection closed")

def main():
    """Main execution"""
    loader = SQLiteLoader()
    
    try:
        loader.load()
    except Exception as e:
        logger.error(f"Loading failed: {e}")
        raise
    finally:
        loader.close()

if __name__ == "__main__":
    main()