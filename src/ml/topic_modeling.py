"""
Topic Modeling Module (Optional)
Uses LDA for topic discovery in Reddit discussions
"""

import pandas as pd
from pathlib import Path
import sys
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import numpy as np

sys.path.append(str(Path(__file__).parent.parent.parent))
from config import logger

class TopicModeler:
    """Discover topics using LDA"""
    
    def __init__(self, n_topics=5, n_top_words=10):
        self.n_topics = n_topics
        self.n_top_words = n_top_words
        self.vectorizer = None
        self.lda_model = None
        self.topics = []
        
    def load_data(self, csv_path='data/processed_reddit_data.csv'):
        """Load processed data"""
        try:
            if not Path(csv_path).exists():
                logger.error(f"Data file not found: {csv_path}")
                return None
            
            df = pd.read_csv(csv_path)
            logger.info(f"Loaded {len(df)} records for topic modeling")
            
            return df
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return None
    
    def prepare_texts(self, df):
        """Prepare texts for topic modeling"""
        if 'full_text' in df.columns:
            texts = df['full_text'].fillna('').tolist()
        else:
            texts = (df['title_clean'].fillna('') + ' ' + df['body_clean'].fillna('')).tolist()
        
        # Filter out very short texts
        texts = [t for t in texts if len(t) > 20]
        
        logger.info(f"Prepared {len(texts)} texts for modeling")
        return texts
    
    def fit_lda(self, texts):
        """Fit LDA topic model"""
        try:
            logger.info("Fitting LDA model...")
            
            # Create document-term matrix
            self.vectorizer = CountVectorizer(
                max_features=1000,
                min_df=2,
                max_df=0.8,
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            doc_term_matrix = self.vectorizer.fit_transform(texts)
            
            # Fit LDA
            self.lda_model = LatentDirichletAllocation(
                n_components=self.n_topics,
                random_state=42,
                max_iter=20,
                learning_method='online',
                n_jobs=-1
            )
            
            self.lda_model.fit(doc_term_matrix)
            
            logger.success("✓ LDA model fitted successfully")
            return doc_term_matrix
            
        except Exception as e:
            logger.error(f"Error fitting LDA: {e}")
            return None
    
    def extract_topics(self):
        """Extract top words for each topic"""
        try:
            feature_names = self.vectorizer.get_feature_names_out()
            
            for topic_idx, topic in enumerate(self.lda_model.components_):
                top_indices = topic.argsort()[-self.n_top_words:][::-1]
                top_words = [feature_names[i] for i in top_indices]
                
                topic_info = {
                    'topic_id': topic_idx,
                    'top_words': top_words,
                    'label': self._assign_topic_label(top_words)
                }
                
                self.topics.append(topic_info)
                
                logger.info(f"  Topic {topic_idx}: {', '.join(top_words[:5])}")
            
            return self.topics
            
        except Exception as e:
            logger.error(f"Error extracting topics: {e}")
            return []
    
    def _assign_topic_label(self, top_words):
        """Assign human-readable label to topic based on top words"""
        # Simple heuristic-based labeling
        words_str = ' '.join(top_words).lower()
        
        if any(word in words_str for word in ['price', 'cost', 'budget', 'pricing']):
            return 'Pricing & Budget'
        elif any(word in words_str for word in ['feature', 'tool', 'platform', 'software']):
            return 'Features & Tools'
        elif any(word in words_str for word in ['integration', 'api', 'connect', 'data']):
            return 'Integration & Data'
        elif any(word in words_str for word in ['competitor', 'alternative', 'vs', 'comparison']):
            return 'Competitive Analysis'
        elif any(word in words_str for word in ['roi', 'analytics', 'metrics', 'performance']):
            return 'Analytics & ROI'
        else:
            return 'General Discussion'
    
    def assign_topics_to_posts(self, texts, df):
        """Assign dominant topic to each post"""
        try:
            doc_term_matrix = self.vectorizer.transform(texts)
            topic_distributions = self.lda_model.transform(doc_term_matrix)
            
            # Get dominant topic for each document
            dominant_topics = np.argmax(topic_distributions, axis=1)
            
            # Add to dataframe
            df['topic_id'] = dominant_topics
            df['topic_label'] = df['topic_id'].map(
                lambda x: self.topics[x]['label'] if x < len(self.topics) else 'Unknown'
            )
            
            logger.info("✓ Assigned topics to posts")
            return df
            
        except Exception as e:
            logger.error(f"Error assigning topics: {e}")
            return df
    
    def save_results(self, df, output_path='data/topic_modeling_results.csv'):
        """Save topic modeling results"""
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            df.to_csv(output_path, index=False)
            logger.success(f"✅ Saved results to {output_path}")
            
            # Display topic distribution
            self._display_summary(df)
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving results: {e}")
            return False
    
    def _display_summary(self, df):
        """Display topic modeling summary"""
        logger.info("\n📊 Topic Modeling Summary:")
        
        topic_dist = df['topic_label'].value_counts()
        logger.info("\n  Topic Distribution:")
        for label, count in topic_dist.items():
            percentage = (count / len(df)) * 100
            logger.info(f"    {label}: {count} ({percentage:.1f}%)")
    
    def run(self):
        """Main topic modeling workflow"""
        logger.info("Starting topic modeling...")
        
        # Load data
        df = self.load_data()
        if df is None:
            return False
        
        # Prepare texts
        texts = self.prepare_texts(df)
        
        # Fit LDA
        if self.fit_lda(texts) is None:
            return False
        
        # Extract topics
        self.extract_topics()
        
        # Assign topics to posts
        df_with_topics = self.assign_topics_to_posts(texts, df)
        
        # Save results
        self.save_results(df_with_topics)
        
        logger.success("✅ Topic modeling complete!")
        return True

def main():
    """Main execution"""
    modeler = TopicModeler(n_topics=5, n_top_words=10)
    
    try:
        modeler.run()
    except Exception as e:
        logger.error(f"Topic modeling failed: {e}")
        raise

if __name__ == "__main__":
    main()