"""
Sentiment Analysis Module
Uses HuggingFace Transformers for sentiment classification
"""

import pandas as pd
from pathlib import Path
import sys
from transformers import pipeline
import torch
from tqdm import tqdm

sys.path.append(str(Path(__file__).parent.parent.parent))
from config import ML_CONFIG, logger

class SentimentAnalyzer:
    """Analyze sentiment of Reddit posts using Transformers"""
    
    def __init__(self):
        self.model = None
        self.device = ML_CONFIG['device']
        
    def load_model(self):
        """Load pre-trained sentiment analysis model"""
        try:
            logger.info(f"Loading sentiment model: {ML_CONFIG['sentiment_model']}")
            
            # Check if CUDA is available
            if torch.cuda.is_available():
                self.device = 'cuda'
                logger.info("✓ GPU available - using CUDA")
            else:
                self.device = 'cpu'
                logger.info("Using CPU for inference")
            
            # Load pipeline
            self.model = pipeline(
                "sentiment-analysis",
                model=ML_CONFIG['sentiment_model'],
                device=0 if self.device == 'cuda' else -1
            )
            
            logger.success("✓ Sentiment model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    def load_data(self, csv_path='data/processed_reddit_data.csv'):
        """Load processed data"""
        try:
            if not Path(csv_path).exists():
                logger.error(f"Data file not found: {csv_path}")
                return None
            
            df = pd.read_csv(csv_path)
            logger.info(f"Loaded {len(df)} records for sentiment analysis")
            
            return df
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return None
    
    def preprocess_text(self, text):
        """Preprocess text for model input"""
        if not isinstance(text, str):
            return ""
        
        # Truncate to max length
        max_length = ML_CONFIG['max_length']
        if len(text) > max_length:
            text = text[:max_length]
        
        return text
    
    def analyze_sentiment(self, texts, batch_size=16):
        """
        Analyze sentiment for a list of texts
        Returns list of dicts with label and score
        """
        try:
            results = []
            
            # Process in batches with progress bar
            for i in tqdm(range(0, len(texts), batch_size), desc="Analyzing sentiment"):
                batch = texts[i:i + batch_size]
                
                # Preprocess batch
                batch_processed = [self.preprocess_text(text) for text in batch]
                
                # Get predictions
                predictions = self.model(batch_processed)
                results.extend(predictions)
            
            return results
            
        except Exception as e:
            logger.error(f"Error during sentiment analysis: {e}")
            return None
    
    def process_results(self, df, sentiment_results):
        """Process and add sentiment results to dataframe"""
        try:
            # Extract labels and scores
            df['sentiment_label'] = [r['label'] for r in sentiment_results]
            df['sentiment_score'] = [r['score'] for r in sentiment_results]
            
            # Normalize labels (DistilBERT uses POSITIVE/NEGATIVE)
            # Convert to more readable format
            label_map = {
                'POSITIVE': 'POSITIVE',
                'NEGATIVE': 'NEGATIVE',
                'NEUTRAL': 'NEUTRAL'
            }
            
            df['sentiment_label'] = df['sentiment_label'].map(
                lambda x: label_map.get(x, x)
            )
            
            # Add sentiment category based on score
            df['sentiment_category'] = df.apply(
                lambda row: self._categorize_sentiment(row['sentiment_label'], row['sentiment_score']),
                axis=1
            )
            
            logger.info("✓ Processed sentiment results")
            return df
            
        except Exception as e:
            logger.error(f"Error processing results: {e}")
            return df
    
    def _categorize_sentiment(self, label, score):
        """Categorize sentiment with confidence threshold"""
        if score < 0.6:
            return 'NEUTRAL'
        return label
    
    def save_results(self, df, output_path='data/sentiment_results.csv'):
        """Save sentiment analysis results"""
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save full results
            df.to_csv(output_path, index=False)
            logger.success(f"✅ Saved results to {output_path}")
            
            # Display summary statistics
            self._display_summary(df)
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")
            return False
    
    def _display_summary(self, df):
        """Display sentiment analysis summary"""
        logger.info("\n📊 Sentiment Analysis Summary:")
        logger.info(f"  Total posts analyzed: {len(df)}")
        
        # Sentiment distribution
        sentiment_dist = df['sentiment_label'].value_counts()
        logger.info("\n  Sentiment Distribution:")
        for label, count in sentiment_dist.items():
            percentage = (count / len(df)) * 100
            logger.info(f"    {label}: {count} ({percentage:.1f}%)")
        
        # Average sentiment score
        avg_score = df['sentiment_score'].mean()
        logger.info(f"\n  Average confidence score: {avg_score:.3f}")
        
        # Top positive posts
        top_positive = df.nlargest(3, 'sentiment_score')[['title', 'sentiment_label', 'sentiment_score']]
        logger.info("\n  Top 3 most positive posts:")
        for _, row in top_positive.iterrows():
            logger.info(f"    • {row['title'][:60]}... ({row['sentiment_score']:.3f})")
        
        # Sentiment by subreddit
        if 'subreddit' in df.columns:
            sentiment_by_sub = df.groupby('subreddit')['sentiment_label'].value_counts().unstack(fill_value=0)
            logger.info("\n  Sentiment by Subreddit:")
            logger.info(f"\n{sentiment_by_sub}")
    
    def analyze(self):
        """Main analysis workflow"""
        logger.info("Starting sentiment analysis...")
        
        # Load model
        if not self.load_model():
            return False
        
        # Load data
        df = self.load_data()
        if df is None:
            return False
        
        # Prepare texts for analysis
        # Use full_text if available, otherwise combine title and body
        if 'full_text' in df.columns:
            texts = df['full_text'].fillna('').tolist()
        else:
            texts = (df['title'].fillna('') + ' ' + df['body'].fillna('')).tolist()
        
        logger.info(f"Analyzing {len(texts)} texts...")
        
        # Analyze sentiment
        sentiment_results = self.analyze_sentiment(texts, batch_size=ML_CONFIG['batch_size'])
        
        if sentiment_results is None:
            return False
        
        # Process results
        df_with_sentiment = self.process_results(df, sentiment_results)
        
        # Save results
        self.save_results(df_with_sentiment)
        
        logger.success("✅ Sentiment analysis complete!")
        return True

def main():
    """Main execution"""
    analyzer = SentimentAnalyzer()
    
    try:
        analyzer.analyze()
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}")
        raise

if __name__ == "__main__":
    main()
