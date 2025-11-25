"""
Process YouTube comments data
Converts raw YouTube comments into format compatible with sentiment analysis
"""

import json
import pandas as pd
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent))

def load_youtube_data():
    """Load YouTube comments from JSON or MongoDB"""
    # Try JSON first
    json_path = Path(__file__).parent.parent.parent / 'data' / 'youtube_comments.json'
    
    if json_path.exists():
        print(f"📂 Loading from {json_path}")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return pd.DataFrame(data)
    
    print("❌ No YouTube data found!")
    return pd.DataFrame()

def process_youtube_data(df):
    """Process YouTube comments into standardized format"""
    print(f"\n🔄 Processing {len(df)} YouTube comments...")
    
    # Rename columns to match Reddit format for compatibility
    processed = pd.DataFrame({
        'id': df['id'],
        'title': df['text'].str[:100],  # First 100 chars as title
        'body': df['text'],
        'text': df['text'],  # Keep for sentiment analysis
        'author': df['author'],
        'score': df['like_count'],
        'num_comments': df['reply_count'],
        'created_utc': pd.to_datetime(df['published_at']).astype(int) // 10**9,
        'timestamp': df['published_at'],
        'subreddit': df['brand'],  # Brand as "subreddit"
        'video_id': df['video_id'],
        'video_title': df['video_title'],
        'video_channel': df['video_channel'],
        'brand': df['brand'],
        'search_query': df['search_query'],
        'source': df['source'],
        'url': 'https://youtube.com/watch?v=' + df['video_id'],
        'permalink': 'https://youtube.com/watch?v=' + df['video_id'],
    })
    
    # Add engagement score
    processed['engagement_score'] = (
        processed['score'] * 1.0 + 
        processed['num_comments'] * 2.0
    )
    
    # Clean text
    processed['text'] = processed['text'].str.replace(r'http\S+', '', regex=True)
    processed['text'] = processed['text'].str.replace(r'@\w+', '', regex=True)
    processed['text'] = processed['text'].str.strip()
    
    # Remove very short comments (likely spam)
    processed = processed[processed['text'].str.len() >= 10]
    
    print(f"✅ Processed {len(processed)} comments (removed {len(df) - len(processed)} short/spam)")
    
    return processed

def save_processed_data(df):
    """Save processed data"""
    # Save to JSON
    json_path = Path(__file__).parent.parent.parent / 'data' / 'youtube_processed.json'
    json_path.parent.mkdir(parents=True, exist_ok=True)
    
    df.to_json(json_path, orient='records', indent=2, force_ascii=False)
    print(f"✅ Saved to {json_path}")

def generate_statistics(df):
    """Print processing statistics"""
    print("\n" + "="*70)
    print("PROCESSED DATA STATISTICS")
    print("="*70)
    
    print(f"\nTotal comments: {len(df)}")
    
    print("\nBy Brand:")
    for brand, count in df['brand'].value_counts().items():
        print(f"  {brand}: {count}")
    
    print("\nEngagement Statistics:")
    print(f"  Avg likes: {df['score'].mean():.1f}")
    print(f"  Avg replies: {df['num_comments'].mean():.1f}")
    print(f"  Avg engagement score: {df['engagement_score'].mean():.1f}")
    
    print("\nText Length Statistics:")
    text_lengths = df['text'].str.len()
    print(f"  Avg: {text_lengths.mean():.0f} characters")
    print(f"  Min: {text_lengths.min()}")
    print(f"  Max: {text_lengths.max()}")
    
    print("="*70)

def main():
    """Main execution"""
    print("🎬 YOUTUBE DATA PROCESSING")
    print("="*70)
    
    # Load raw data
    df = load_youtube_data()
    
    if df.empty:
        print("❌ No data to process. Run extract_youtube.py first.")
        return
    
    # Process data
    processed_df = process_youtube_data(df)
    
    # Save processed data
    save_processed_data(processed_df)
    
    # Show statistics
    generate_statistics(processed_df)
    
    print("\n✅ PROCESSING COMPLETE!")
    print("\nNext steps:")
    print("1. Run: python src/ml/sentiment_analysis.py")
    print("2. Run: python src/etl/load_to_sqlite.py")
    print("3. Run: streamlit run app.py")

if __name__ == "__main__":
    main()