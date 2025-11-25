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
    create_topic_distribution,
    create_channel_performance_table,
    create_data_source_table_compact,
    create_campaign_table_compact
)

# Page configuration
st.set_page_config(
    page_title="Improvado Marketing Intelligence",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Improvado exact branding
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global Font */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Main background */
    .stApp {
        background-color: #F3F4F6;
    }
    
    .main {
        background-color: #F3F4F6;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #2D2B55;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #E5E7EB;
    }
    
    [data-testid="stSidebar"] h3 {
        color: #9CA3AF;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 20px;
    }
    
    /* Sidebar Radio Buttons */
    .stRadio > label {
        color: #E5E7EB !important;
    }
    
    /* Remove default padding */
    .block-container {
        padding-top: 3rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    
    /* Card Styling */
    .css-card {
        background-color: #FFFFFF;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid #E5E7EB;
        margin-bottom: 1rem;
    }
    
    /* Headers */
    h1 {
        color: #111827;
        font-weight: 700;
        font-size: 24px;
        margin-bottom: 1rem;
    }
    
    h2 {
        color: #374151;
        font-weight: 600;
        font-size: 18px;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    
    h3 {
        color: #4B5563;
        font-weight: 600;
        font-size: 14px;
        margin-bottom: 0.5rem;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        border: none !important;
    }
    
    /* Custom Metric Card */
    .metric-card {
        background-color: white;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        border: 1px solid #E5E7EB;
        height: 100%;
    }
    
    .metric-label {
        color: #6B7280;
        font-size: 12px;
        font-weight: 500;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    
    .metric-value {
        color: #111827;
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 4px;
    }
    
    .metric-delta {
        font-size: 12px;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 2px;
    }
    
    .delta-pos { color: #10B981; }
    .delta-neg { color: #EF4444; }
    
    /* Top Navigation Bar (Mock) */
    .nav-bar {
        display: flex;
        gap: 10px;
        margin-bottom: 20px;
        flex-wrap: wrap;
        padding-top: 10px;
    }
    
    .nav-item {
        background-color: #2D2B55;
        color: white;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 12px;
        display: flex;
        align-items: center;
        gap: 6px;
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
def load_youtube_data(_conn):
    """Load YouTube comments data"""
    try:
        query = "SELECT * FROM youtube_processed ORDER BY timestamp DESC"
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
    # Initialize session state for chart selection
    if 'selected_chart' not in st.session_state:
        st.session_state.selected_chart = 'channel'

    # Top Navigation Bar (Mock)
    st.markdown("""
    <div class="nav-bar">
        <div class="nav-item">Data Source ▾</div>
        <div class="nav-item">Channel ▾</div>
        <div class="nav-item">Campaign ▾</div>
        <div class="nav-item">Ad Set ▾</div>
        <div class="nav-item">Jan 1, 2023 - Mar 31, 2023 ▾</div>
    </div>
    """, unsafe_allow_html=True)
    
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
    
    # Main Layout: Center content (65%) + Right sidebar (35%)
    center_col, right_sidebar = st.columns([6.5, 3.5])
    
    with center_col:
        # ============= TOP: KPI CARDS (2 rows x 4 columns) =============
        # Row 1
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            kpi = kpis.get('spend', {})
            create_kpi_card("Spend", kpi.get('value', 0), kpi.get('unit', ''), kpi.get('change', 0), kpi.get('change_unit', ''), sparkline_data=generate_sparkline_data())
        with col2:
            kpi = kpis.get('cpm', {})
            create_kpi_card("CPM", kpi.get('value', 0), kpi.get('unit', ''), kpi.get('change', 0), kpi.get('change_unit', ''), sparkline_data=generate_sparkline_data())
        with col3:
            kpi = kpis.get('ctr', {})
            create_kpi_card("CTR", kpi.get('value', 0), kpi.get('unit', ''), kpi.get('change', 0), kpi.get('change_unit', ''), sparkline_data=generate_sparkline_data())
        with col4:
            kpi = kpis.get('cpc', {})
            create_kpi_card("CPC", kpi.get('value', 0), kpi.get('unit', ''), kpi.get('change', 0), kpi.get('change_unit', ''), sparkline_data=generate_sparkline_data())
        
        # Row 2
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            kpi = kpis.get('video_views', {})
            create_kpi_card("Video Views", kpi.get('value', 0), kpi.get('unit', ''), kpi.get('change', 0), kpi.get('change_unit', ''), sparkline_data=generate_sparkline_data())
        with col6:
            kpi = kpis.get('impressions', {})
            create_kpi_card("Impressions", kpi.get('value', 0), kpi.get('unit', ''), kpi.get('change', 0), kpi.get('change_unit', ''), sparkline_data=generate_sparkline_data())
        with col7:
            kpi = kpis.get('conversions', {})
            create_kpi_card("Conversions", kpi.get('value', 0), kpi.get('unit', ''), kpi.get('change', 0), kpi.get('change_unit', ''), sparkline_data=generate_sparkline_data())
        with col8:
            kpi = kpis.get('conversion_rate', {})
            create_kpi_card("Conversion Rate", kpi.get('value', 0), kpi.get('unit', ''), kpi.get('change', 0), kpi.get('change_unit', ''), sparkline_data=generate_sparkline_data())
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # ============= CENTER: TIME SERIES CHART =============
        # Wrap chart in a card container
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        
        selected_chart = st.session_state.get('selected_chart', 'channel')
        
        if selected_chart == 'channel':
            time_series = load_time_series(conn)
            if not time_series.empty:
                create_time_series_chart(time_series, group_col='channel', value_col='value', title="Channel Performance Over Time")
        elif selected_chart == 'source':
            data_sources = load_data_source_performance(conn)
            if not data_sources.empty:
                create_time_series_chart(data_sources, group_col='source', value_col='impressions', title="Data Source Performance")
        elif selected_chart == 'campaign':
            campaigns = load_campaign_performance(conn)
            if not campaigns.empty:
                create_time_series_chart(campaigns, group_col='campaign', value_col='impressions', title="Campaign Performance")
                
        st.markdown('</div>', unsafe_allow_html=True)

        # Load data for sidebar usage (tables removed from center view)
        data_sources = load_data_source_performance(conn)
        campaigns = load_campaign_performance(conn)
        
    
    # ============= RIGHT SIDEBAR: 3 TABLES STACKED =============
    with right_sidebar:
        # Channel Performance
        channels = load_channel_performance(conn)
        if not channels.empty:
            create_channel_performance_table(channels)
        
        # Data Source Performance (compact version for sidebar)
        if not data_sources.empty:
            create_data_source_table_compact(data_sources)
        
        # Campaign Performance (compact version for sidebar)
        if not campaigns.empty:
            create_campaign_table_compact(campaigns)

def render_ai_customer_voice(conn):
    """Render AI Customer Voice section"""
    st.markdown('<div class="sub-header" style="margin-top: 30px;">AI Customer Voice (YouTube)</div>', unsafe_allow_html=True)
    
    df = load_youtube_data(conn)
    
    if df.empty:
        st.info("No YouTube data available. Run the ETL pipeline to collect data.")
        return

    # --- Filters ---
    st.markdown('<div style="margin-bottom: 20px;">', unsafe_allow_html=True)
    filter_col1, filter_col2 = st.columns([1, 1])
    
    with filter_col1:
        # Brand Filter
        brands = ['All'] + sorted(df['brand'].unique().tolist())
        selected_brand = st.selectbox("Select Brand", brands, index=0)
    
    with filter_col2:
        # Sentiment Filter (for comments list)
        sentiments = ['POSITIVE', 'NEGATIVE', 'NEUTRAL']
        selected_sentiments = st.multiselect("Filter Comments by Sentiment", sentiments, default=sentiments)
        
    st.markdown('</div>', unsafe_allow_html=True)

    # Apply Filters
    # 1. Brand Filter applies to EVERYTHING (Charts + Comments)
    if selected_brand != 'All':
        df_filtered = df[df['brand'] == selected_brand]
    else:
        df_filtered = df
        
    # 2. Sentiment Filter applies ONLY to the Comments List
    if selected_sentiments:
        df_comments = df_filtered[df_filtered['sentiment_label'].isin(selected_sentiments)]
    else:
        df_comments = df_filtered

    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.markdown("### Sentiment Distribution")
        # Chart uses Brand-filtered data (shows distribution for that brand)
        create_sentiment_distribution_chart(df_filtered)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.markdown("### Recent Comments")
        
        # Comments list uses Brand AND Sentiment filtered data
        for _, row in df_comments.head(5).iterrows():
            sentiment_color = {
                'POSITIVE': '#10B981',
                'NEGATIVE': '#EF4444',
                'NEUTRAL': '#6B7280'
            }.get(row.get('sentiment_label', 'NEUTRAL'), '#6B7280')
            
            st.markdown(f"""
            <div style="padding: 10px; border-bottom: 1px solid #eee;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                    <span style="font-weight: 600; color: #1F2937;">{row.get('author', 'Unknown')}</span>
                    <span style="background-color: {sentiment_color}20; color: {sentiment_color}; padding: 2px 8px; border-radius: 12px; font-size: 12px;">
                        {row.get('sentiment_label', 'NEUTRAL')}
                    </span>
                </div>
                <div style="font-size: 12px; color: #6B7280; margin-bottom: 5px;">
                    on <b>{row.get('video_title', 'Unknown Video')}</b> ({row.get('video_channel', 'Unknown Channel')})
                </div>
                <div style="color: #4B5563; font-size: 14px;">{row.get('text', '')}</div>
                <div style="font-size: 12px; color: #9CA3AF; margin-top: 5px;">
                    👍 {row.get('score', 0)} • 💬 {row.get('num_comments', 0)} replies
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Main application"""
    
    # Sidebar
    with st.sidebar:
        # Logo
        st.image("img/improvado_logo.png", width=160)
        
        st.markdown("### Navigation")
        
        page = st.radio(
            "Select Dashboard",
            ["📊 Executive Summary", "🤖 AI Customer Voice"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        <div style='font-size: 13px; line-height: 1.6;'>
        This PoC demonstrates:<br>
        • Real-time marketing analytics<br>
        • AI-powered sentiment analysis<br>
        • Data engineering excellence<br>
        • Production-ready architecture
        </div>
        """, unsafe_allow_html=True)
        
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
