"""
Reusable Streamlit Dashboard Components
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def create_kpi_card(title, value, unit, change, change_unit, sparkline_data=None):
    """
    Create a KPI card with metric, change indicator, and sparkline
    
    Args:
        title: KPI title (e.g., "Spend", "CTR")
        value: Main metric value
        unit: Unit suffix (e.g., "M", "K", "%")
        change: Change value
        change_unit: Change unit
        sparkline_data: List of values for sparkline chart
    """
    # Format the value with unit
    if unit:
        display_value = f"${value}{unit}" if title in ["Spend", "CPM", "CPC"] else f"{value}{unit}"
    else:
        display_value = str(value)
    
    # Format the change
    if change_unit:
        delta_text = f"+{change}{change_unit}" if change >= 0 else f"{change}{change_unit}"
    else:
        delta_text = f"+{change}" if change >= 0 else f"{change}"
    
    # Determine delta color
    delta_color = "normal" if change >= 0 else "inverse"
    
    # Display metric
    st.metric(
        label=title,
        value=display_value,
        delta=delta_text,
        delta_color=delta_color
    )
    
    # Add sparkline if data provided
    if sparkline_data and len(sparkline_data) > 0:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            y=sparkline_data,
            mode='lines',
            line=dict(color='#8B5CF6', width=2),
            fill='tozeroy',
            fillcolor='rgba(139, 92, 246, 0.2)'
        ))
        fig.update_layout(
            height=80,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def create_performance_table(df, title):
    """
    Create a styled performance table
    
    Args:
        df: DataFrame with performance data
        title: Table title
    """
    st.markdown(f"### {title}")
    
    # Style the dataframe
    styled_df = df.style.format({
        'Impressions': '{:.1f}K',
        '% Δ': lambda x: f"{x:+.1f}%" if pd.notna(x) else "-",
        'CTR': '{:.2f}%',
        '% Δ.1': lambda x: f"{x:+.1f}%" if pd.notna(x) else "-"
    })
    
    st.dataframe(styled_df, use_container_width=True, hide_index=True)

def create_time_series_chart(df, title="Channel Performance Over Time"):
    """
    Create multi-line time series chart
    
    Args:
        df: DataFrame with columns: date, channel, value
        title: Chart title
    """
    fig = go.Figure()
    
    # Color mapping for channels
    colors = {
        'Programmatic': '#6366F1',  # Indigo
        'Paid Search': '#EC4899',   # Pink
        'Paid Social': '#8B5CF6',   # Purple
        'Organic': '#F59E0B'         # Amber
    }
    
    channels = df['channel'].unique()
    
    for channel in channels:
        channel_data = df[df['channel'] == channel].sort_values('date')
        
        fig.add_trace(go.Scatter(
            x=channel_data['date'],
            y=channel_data['value'],
            mode='lines+markers',
            name=channel,
            line=dict(color=colors.get(channel, '#6366F1'), width=2),
            marker=dict(size=6)
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title="",
        yaxis_title="",
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=400,
        margin=dict(l=50, r=50, t=80, b=50),
        paper_bgcolor='white',
        plot_bgcolor='#F9FAFB'
    )
    
    # Update axes
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#E5E7EB')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#E5E7EB')
    
    st.plotly_chart(fig, use_container_width=True)

def create_sentiment_distribution_chart(df):
    """Create sentiment distribution pie/bar chart"""
    sentiment_counts = df['sentiment_label'].value_counts()
    
    fig = go.Figure(data=[go.Pie(
        labels=sentiment_counts.index,
        values=sentiment_counts.values,
        hole=0.4,
        marker=dict(colors=['#10B981', '#EF4444', '#6B7280'])
    )])
    
    fig.update_layout(
        title="Sentiment Distribution",
        height=350,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_sentiment_timeline(df):
    """Create sentiment trend over time"""
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    
    sentiment_by_date = df.groupby(['date', 'sentiment_label']).size().reset_index(name='count')
    
    fig = px.area(
        sentiment_by_date,
        x='date',
        y='count',
        color='sentiment_label',
        title="Sentiment Trend Over Time",
        color_discrete_map={
            'POSITIVE': '#10B981',
            'NEGATIVE': '#EF4444',
            'NEUTRAL': '#6B7280'
        }
    )
    
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

def create_engagement_sentiment_scatter(df):
    """Create scatter plot of engagement vs sentiment"""
    fig = px.scatter(
        df,
        x='sentiment_score',
        y='engagement_score',
        color='sentiment_label',
        size='score',
        hover_data=['title', 'subreddit'],
        title="Engagement vs Sentiment Analysis",
        color_discrete_map={
            'POSITIVE': '#10B981',
            'NEGATIVE': '#EF4444',
            'NEUTRAL': '#6B7280'
        }
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def create_subreddit_sentiment_heatmap(df):
    """Create heatmap of sentiment by subreddit"""
    pivot_data = df.groupby(['subreddit', 'sentiment_label']).size().unstack(fill_value=0)
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_data.values,
        x=pivot_data.columns,
        y=pivot_data.index,
        colorscale='Purples',
        text=pivot_data.values,
        texttemplate='%{text}',
        textfont={"size": 12}
    ))
    
    fig.update_layout(
        title="Sentiment Distribution by Subreddit",
        height=350
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_critical_alerts(df, threshold=0.3):
    """Display critical negative sentiment alerts"""
    st.markdown("### 🚨 Critical Alerts")
    
    # Filter highly negative posts
    critical_posts = df[
        (df['sentiment_label'] == 'NEGATIVE') & 
        (df['sentiment_score'] > threshold)
    ].sort_values('sentiment_score', ascending=False)
    
    if len(critical_posts) > 0:
        st.warning(f"Found {len(critical_posts)} posts with strong negative sentiment")
        
        # Display top 5
        for idx, row in critical_posts.head(5).iterrows():
            with st.expander(f"📍 r/{row['subreddit']} - Score: {row['sentiment_score']:.3f}"):
                st.markdown(f"**Title:** {row['title']}")
                st.markdown(f"**Score:** {row['score']} | **Comments:** {row['num_comments']}")
                st.markdown(f"**Link:** {row.get('permalink', '#')}")
    else:
        st.success("No critical negative sentiment detected")

def create_topic_distribution(df):
    """Create topic distribution chart"""
    if 'topic_label' not in df.columns:
        st.info("Topic modeling data not available")
        return
    
    topic_counts = df['topic_label'].value_counts()
    
    fig = go.Figure(data=[go.Bar(
        x=topic_counts.values,
        y=topic_counts.index,
        orientation='h',
        marker=dict(color='#8B5CF6')
    )])
    
    fig.update_layout(
        title="Discussion Topics Distribution",
        xaxis_title="Number of Posts",
        yaxis_title="",
        height=350
    )
    
    st.plotly_chart(fig, use_container_width=True)