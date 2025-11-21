"""
Improvado Marketing Intelligence Dashboard
Main Streamlit Application
"""

import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent))
from config import SQLITE_CONFIG
from src.dashboard.components import (
    create_kpi_card, 
    create_time_series_chart,
    create_sentiment_distribution_chart,
    create_sentiment_timeline,
    create_engagement_sentiment_scatter,
    create_subreddit_sentiment_heatmap,
    display_critical_alerts,
    create_topic_distribution
)

# Page configuration
st.set_page_config(
    page_title="Improvado Marketing Intelligence",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Improvado branding
st.markdown("""
<style>
    .main {
        background-color: #F9FAFB;
    }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    h1 {
        color: #1F2937;
        font-weight: 700;
    }
    h2, h3 {
        color: #374151;
    }
    .sidebar .sidebar-content {
        background-color: #1F2937;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def init_database():
    """Initialize database connection"""
    try:
        db_path = Path(SQLITE_CONFIG['db_path'])
        if not db_path.exists():
            st.warning(f"Database not found at {db_path}. Please run data generation scripts first.")
            return None
        
        conn = sqlite3.connect(SQLITE_CONFIG['db_path'], check_same_thread=False)
        return conn
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

@st.cache_data
def load_kpi_data(_conn):
    """Load KPI metrics"""
    try:
        query = "SELECT * FROM marketing_kpis ORDER BY date DESC LIMIT 8"
        df = pd.read_sql_query(query, _conn)
        return df
    except Exception as e:
        st.error(f"Error loading KPI data: {e}")
        return pd.DataFrame()

@st.cache_data
def load_channel_performance(_conn):
    """Load channel performance data"""
    try:
        query = "SELECT * FROM channel_performance ORDER BY date DESC"
        df = pd.read_sql_query(query, _conn)
        return df
    except Exception as e:
        st.error(f"Error loading channel data: {e}")
        return pd.DataFrame()

@st.cache_data
def load_data_source_performance(_conn):
    """Load data source performance"""
    try:
        query = "SELECT * FROM data_source_performance ORDER BY date DESC"
        df = pd.read_sql_query(query, _conn)
        return df
    except Exception:
        return pd.DataFrame()

@st.cache_data
def load_campaign_performance(_conn):
    """Load campaign performance"""
    try:
        query = "SELECT * FROM campaign_performance ORDER BY date DESC"
        df = pd.read_sql_query(query, _conn)
        return df
    except Exception:
        return pd.DataFrame()

@st.cache_data
def load_time_series(_conn):
    """Load time series data"""
    try:
        query = "SELECT * FROM time_series_data ORDER BY date"
        df = pd.read_sql_query(query, _conn)
        return df
    except Exception:
        return pd.DataFrame()

@st.cache_data
def load_reddit_data(_conn):
    """Load processed Reddit data"""
    try:
        query = "SELECT * FROM reddit_processed"
        df = pd.read_sql_query(query, _conn)
        return df
    except Exception:
        return pd.DataFrame()

def generate_sparkline_data():
    """Generate simple sparkline data"""
    import random
    return [random.uniform(0.8, 1.2) for _ in range(12)]

def render_executive_summary(conn):
    """Render Executive Summary dashboard"""
    st.title("📊 Executive Summary")
    
    # Load data
    kpi_data = load_kpi_data(conn)
    
    if kpi_data.empty:
        st.warning("No KPI data available. Please run: `python src/etl/generate_kpi_data.py`")
        return
    
    # Convert to dictionary for easy access
    kpis = {}
    for _, row in kpi_data.iterrows():
        kpis[row['metric_name']] = {
            'value': row['metric_value'],
            'unit': row['metric_unit'],
            'change': row['change_value'],
            'change_unit': row['change_unit']
        }
    
    # Top KPI Cards (4 columns)
    st.markdown("### Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        kpi = kpis.get('spend', {})
        create_kpi_card(
            "Spend", 
            kpi.get('value', 0), 
            kpi.get('unit', ''), 
            kpi.get('change', 0), 
            kpi.get('change_unit', ''),
            sparkline_data=generate_sparkline_data()
        )
    
    with col2:
        kpi = kpis.get('cpm', {})
        create_kpi_card(
            "CPM", 
            kpi.get('value', 0), 
            kpi.get('unit', ''), 
            kpi.get('change', 0), 
            kpi.get('change_unit', ''),
            sparkline_data=generate_sparkline_data()
        )
    
    with col3:
        kpi = kpis.get('ctr', {})
        create_kpi_card(
            "CTR", 
            kpi.get('value', 0), 
            kpi.get('unit', ''), 
            kpi.get('change', 0), 
            kpi.get('change_unit', ''),
            sparkline_data=generate_sparkline_data()
        )
    
    with col4:
        kpi = kpis.get('cpc', {})
        create_kpi_card(
            "CPC", 
            kpi.get('value', 0), 
            kpi.get('unit', ''), 
            kpi.get('change', 0), 
            kpi.get('change_unit', ''),
            sparkline_data=generate_sparkline_data()
        )
    
    # Bottom KPI Cards (4 columns)
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        kpi = kpis.get('video_views', {})
        create_kpi_card(
            "Video Views", 
            kpi.get('value', 0), 
            kpi.get('unit', ''), 
            kpi.get('change', 0), 
            kpi.get('change_unit', ''),
            sparkline_data=generate_sparkline_data()
        )
    
    with col6:
        kpi = kpis.get('impressions', {})
        create_kpi_card(
            "Impressions", 
            kpi.get('value', 0), 
            kpi.get('unit', ''), 
            kpi.get('change', 0), 
            kpi.get('change_unit', ''),
            sparkline_data=generate_sparkline_data()
        )
    
    with col7:
        kpi = kpis.get('conversions', {})
        create_kpi_card(
            "Conversions", 
            kpi.get('value', 0), 
            kpi.get('unit', ''), 
            kpi.get('change', 0), 
            kpi.get('change_unit', ''),
            sparkline_data=generate_sparkline_data()
        )
    
    with col8:
        kpi = kpis.get('conversion_rate', {})
        create_kpi_card(
            "Conversion Rate", 
            kpi.get('value', 0), 
            kpi.get('unit', ''), 
            kpi.get('change', 0), 
            kpi.get('change_unit', ''),
            sparkline_data=generate_sparkline_data()
        )
    
    st.markdown("---")
    
    # Main content area
    main_col, sidebar_col = st.columns([2, 1])
    
    with main_col:
        # Time series chart
        time_series = load_time_series(conn)
        if not time_series.empty:
            create_time_series_chart(time_series)
        
        # Data Source Performance
        data_sources = load_data_source_performance(conn)
        if not data_sources.empty:
            st.markdown("### 📊 Data Source Performance")
            st.dataframe(data_sources[['source', 'impressions', 'spend_pct', 'ctr', 'conversions_pct']], 
                        use_container_width=True, hide_index=True)
        
        # Campaign Performance
        campaigns = load_campaign_performance(conn)
        if not campaigns.empty:
            st.markdown("### 🎯 Campaign Performance")
            st.dataframe(campaigns[['campaign', 'impressions', 'ctr']], 
                        use_container_width=True, hide_index=True)
    
    with sidebar_col:
        # Channel Performance
        channels = load_channel_performance(conn)
        if not channels.empty:
            st.markdown("### 📺 Channel Performance")
            st.dataframe(channels[['channel', 'impressions', 'spend_pct', 'ctr']], 
                        use_container_width=True, hide_index=True)

def render_ai_customer_voice(conn):
    """Render AI Customer Voice dashboard"""
    st.title("🤖 AI Customer Voice Analysis")
    
    st.markdown("""
    ### Real-time Customer Sentiment Monitoring
    *Enables proactive marketing strategy adjustments, potentially improving campaign ROI by 15-25%*
    """)
    
    # Load Reddit data
    reddit_data = load_reddit_data(conn)
    
    if reddit_data.empty:
        st.info("""
        **No customer voice data available yet.**
        
        To populate this dashboard:
        1. Configure Reddit API credentials in `.env`
        2. Run: `python src/etl/extract_reddit.py`
        3. Run: `python src/etl/process_data.py`
        4. Run: `python src/ml/sentiment_analysis.py`
        5. Run: `python src/etl/load_to_sqlite.py`
        
        Or use demo mode with sample data.
        """)
        return
    
    # Check if sentiment analysis is available
    if 'sentiment_label' not in reddit_data.columns:
        st.warning("Sentiment analysis not yet performed. Run: `python src/ml/sentiment_analysis.py`")
        return
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_posts = len(reddit_data)
        st.metric("Total Posts Analyzed", f"{total_posts:,}")
    
    with col2:
        positive_pct = (reddit_data['sentiment_label'] == 'POSITIVE').sum() / total_posts * 100
        st.metric("Positive Sentiment", f"{positive_pct:.1f}%")
    
    with col3:
        negative_pct = (reddit_data['sentiment_label'] == 'NEGATIVE').sum() / total_posts * 100
        st.metric("Negative Sentiment", f"{negative_pct:.1f}%", 
                 delta=f"{negative_pct:.1f}%", delta_color="inverse")
    
    with col4:
        avg_engagement = reddit_data['score'].mean()
        st.metric("Avg Engagement Score", f"{avg_engagement:.1f}")
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        create_sentiment_distribution_chart(reddit_data)
    
    with col2:
        if 'timestamp' in reddit_data.columns:
            create_sentiment_timeline(reddit_data)
    
    # Subreddit analysis
    col1, col2 = st.columns(2)
    
    with col1:
        create_subreddit_sentiment_heatmap(reddit_data)
    
    with col2:
        if 'engagement_score' in reddit_data.columns:
            create_engagement_sentiment_scatter(reddit_data)
    
    # Topic distribution
    if 'topic_label' in reddit_data.columns:
        create_topic_distribution(reddit_data)
    
    # Critical alerts
    display_critical_alerts(reddit_data)
    
    # Data table
    with st.expander("📋 View Raw Data"):
        display_cols = ['subreddit', 'title', 'score', 'sentiment_label', 'sentiment_score']
        available_cols = [col for col in display_cols if col in reddit_data.columns]
        st.dataframe(reddit_data[available_cols].head(50), use_container_width=True)

def main():
    """Main application"""
    
    # Sidebar
    with st.sidebar:
        st.image("https://improvado.io/hubfs/improvado-2021/images/logo.svg", width=150)
        st.title("Navigation")
        
        page = st.radio(
            "Select Dashboard",
            ["📊 Executive Summary", "🤖 AI Customer Voice"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This PoC demonstrates:
        - Real-time marketing analytics
        - AI-powered sentiment analysis
        - Data engineering excellence
        - Production-ready architecture
        """)
        
        st.markdown("---")
        st.markdown("### Data Status")
        
        # Check data availability
        db_path = Path(SQLITE_CONFIG['db_path'])
        if db_path.exists():
            st.success("✅ Database connected")
        else:
            st.error("❌ Database not found")
            st.info("Run: `python src/etl/generate_kpi_data.py`")
    
    # Initialize database
    conn = init_database()
    
    if conn is None:
        st.error("Cannot connect to database. Please check configuration.")
        return
    
    # Render selected page
    if page == "📊 Executive Summary":
        render_executive_summary(conn)
    elif page == "🤖 AI Customer Voice":
        render_ai_customer_voice(conn)

if __name__ == "__main__":
    main()
