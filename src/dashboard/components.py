"""
Reusable Streamlit Dashboard Components - Improvado Style
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Improvado color palette
COLORS = {
    'primary': '#6E4AE7',      # Purple
    'secondary': '#EC4899',    # Pink
    'tertiary': '#3B82F6',     # Blue
    'success': '#10B981',      # Green
    'warning': '#F59E0B',      # Amber
    'danger': '#EF4444',       # Red
    'neutral': '#6B7280',      # Gray
    'background': '#F3F4F6',   # Light gray
    'border': '#E5E7EB',       # Border gray
    'text': '#111827',         # Dark text
    'text_secondary': '#6B7280' # Secondary text
}

def create_kpi_card(title, value, unit, change, change_unit, sparkline_data=None):
    """
    Create a KPI card with metric, change indicator, and sparkline (Improvado style)
    Uses custom HTML/CSS for exact styling control
    """
    # Format value
    if unit:
        if title in ["Spend", "CPM", "CPC"]:
            display_value = f"${value}{unit}"
        else:
            display_value = f"{value}{unit}"
    else:
        display_value = str(value)
    
    # Format change
    if change_unit:
        delta_text = f"{change:+.1f}{change_unit}" if isinstance(change, (int, float)) else f"{change}{change_unit}"
    else:
        delta_text = f"{change:+.1f}" if isinstance(change, (int, float)) else str(change)
    
    # Determine color and icon
    is_positive = change >= 0
    delta_class = "delta-pos" if is_positive else "delta-neg"
    delta_icon = "↑" if is_positive else "↓"
    
    # Generate sparkline plot
    sparkline_html = ""
    if sparkline_data and len(sparkline_data) > 0:
        fig = go.Figure()
        
        line_color = COLORS['primary'] if is_positive else COLORS['danger']
        fill_color = "rgba(110, 74, 231, 0.1)" if is_positive else "rgba(239, 68, 68, 0.1)"
        
        fig.add_trace(go.Scatter(
            y=sparkline_data,
            mode='lines',
            line=dict(color=line_color, width=2),
            fill='tozeroy',
            fillcolor=fill_color,
            hovertemplate='%{y:.2f}<extra></extra>'
        ))
        
        fig.update_layout(
            height=50,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis=dict(visible=False, showgrid=False),
            yaxis=dict(visible=False, showgrid=False),
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            hovermode=False
        )
        
        # We can't easily embed the plotly chart in the HTML string, 
        # so we'll render the card in two parts: HTML header + Plotly chart
    
    # Render the card container start
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{title}</div>
        <div class="metric-value">{display_value}</div>
        <div class="metric-delta {delta_class}">
            {delta_icon} {delta_text}
        </div>
    """, unsafe_allow_html=True)
    
    # Render sparkline if available
    if sparkline_data and len(sparkline_data) > 0:
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'staticPlot': True})
    
    # Close container
    st.markdown("</div>", unsafe_allow_html=True)

def create_time_series_chart(df, group_col='channel', value_col='value', title="Performance Over Time"):
    """Create multi-line time series chart (Improvado style)"""
    fig = go.Figure()
    
    # Dynamic color mapping based on unique values
    unique_groups = df[group_col].unique()
    colors_list = [COLORS['primary'], COLORS['secondary'], COLORS['tertiary'], COLORS['warning'], COLORS['success'], COLORS['danger']]
    colors = {group: colors_list[i % len(colors_list)] for i, group in enumerate(unique_groups)}
    
    for group in unique_groups:
        group_data = df[df[group_col] == group].sort_values('date')
        
        fig.add_trace(go.Scatter(
            x=group_data['date'],
            y=group_data[value_col],
            mode='lines',
            name=group,
            line=dict(color=colors.get(group, COLORS['primary']), width=2),
            hovertemplate=f'<b>{group}</b><br>%{{x}}<br>%{{y:,.0f}}<extra></extra>'
        ))
    
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=14, color='#6B7280', family='Inter, sans-serif'),
            x=0,
            xanchor='left'
        ),
        xaxis_title="",
        yaxis_title="",
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=12, family='Inter, sans-serif'),
            bgcolor='rgba(0,0,0,0)'
        ),
        height=550,
        margin=dict(l=40, r=20, t=40, b=40),
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(family='Inter, sans-serif')
    )
    
    fig.update_xaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='#F3F4F6',
        showline=True,
        linewidth=1,
        linecolor='#E5E7EB',
        tickfont=dict(color='#9CA3AF', size=11)
    )
    fig.update_yaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='#F3F4F6',
        showline=False,
        tickfont=dict(color='#9CA3AF', size=11)
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def create_channel_performance_table(df):
    """Create Channel Performance table (Improvado style)"""
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        st.markdown("<h3 style='color: #4B5563; font-size: 14px; font-weight: 600; margin: 0;'>📺 Channel Performance</h3>", unsafe_allow_html=True)
    with col2:
        if st.button("📈", key="btn_channel", help="Show Channel Graph"):
            st.session_state.selected_chart = 'channel'
            st.rerun()

    display_df = df[['channel', 'impressions', 'spend_pct', 'ctr']].copy()
    display_df.columns = ['Channel', 'Impressions', '% Δ', 'CTR']
    
    display_df['Impressions'] = display_df['Impressions'].apply(lambda x: f"{x:.1f}K" if x < 1000 else f"{x/1000:.1f}M")
    display_df['% Δ'] = display_df['% Δ'].apply(lambda x: f"{x:+.1f}%" if pd.notna(x) else "-")
    display_df['CTR'] = display_df['CTR'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "-")
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Channel": st.column_config.TextColumn("Channel", width="medium"),
            "Impressions": st.column_config.TextColumn("Impressions", width="small"),
            "% Δ": st.column_config.TextColumn("% Δ", width="small"),
            "CTR": st.column_config.TextColumn("CTR", width="small"),
        }
    )
    st.markdown("</div>", unsafe_allow_html=True)

def create_data_source_table(df):
    """Create Data Source Performance table (Improvado style)"""
    st.markdown("""
    <div class="css-card">
        <h3 style='color: #4B5563; font-size: 14px; font-weight: 600; margin: 0 0 16px 0;'>
            📊 Data Source Performance
        </h3>
    """, unsafe_allow_html=True)
    
    display_df = df[['source', 'impressions', 'spend_pct', 'ctr', 'conversions_pct']].copy()
    display_df.columns = ['Source', 'Impressions', '% Δ', 'CTR', '% Δ ']
    
    display_df['Impressions'] = display_df['Impressions'].apply(lambda x: f"{x:.1f}K")
    display_df['% Δ'] = display_df['% Δ'].apply(lambda x: f"{x:+.1f}%" if pd.notna(x) else "-")
    display_df['CTR'] = display_df['CTR'].apply(lambda x: f"{x:.2f}%")
    display_df['% Δ '] = display_df['% Δ '].apply(lambda x: f"{x:+.1f}%" if pd.notna(x) else "-")
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

def create_campaign_table(df):
    """Create Campaign Performance table (Improvado style)"""
    st.markdown("""
    <div class="css-card">
        <h3 style='color: #4B5563; font-size: 14px; font-weight: 600; margin: 0 0 16px 0;'>
            🎯 Campaign Performance
        </h3>
    """, unsafe_allow_html=True)
    
    display_df = df[['campaign', 'impressions', 'ctr']].copy()
    display_df.columns = ['Campaign', 'Impressions', 'CTR']
    
    display_df['Impressions'] = display_df['Impressions'].apply(lambda x: f"{x:.0f}")
    display_df['CTR'] = display_df['CTR'].apply(lambda x: f"{x:.2f}%")
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

def create_data_source_table_compact(df):
    """Create compact Data Source Performance table for right sidebar"""
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        st.markdown("<h3 style='color: #4B5563; font-size: 13px; font-weight: 600; margin: 0;'>📊 Data Source Performance</h3>", unsafe_allow_html=True)
    with col2:
        if st.button("📈", key="btn_source", help="Show Data Source Graph"):
            st.session_state.selected_chart = 'source'
            st.rerun()
    
    # Show only top 5 sources with key metrics
    display_df = df.head(5)[['source', 'impressions', 'ctr']].copy()
    display_df.columns = ['Source', 'Impr.', 'CTR']
    
    # Format values (more compact)
    display_df['Impr.'] = display_df['Impr.'].apply(lambda x: f"{x:.0f}K")
    display_df['CTR'] = display_df['CTR'].apply(lambda x: f"{x:.1f}%")
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=200
    )
    st.markdown("</div>", unsafe_allow_html=True)

def create_campaign_table_compact(df):
    """Create compact Campaign Performance table for right sidebar"""
    st.markdown('<div class="css-card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        st.markdown("<h3 style='color: #4B5563; font-size: 13px; font-weight: 600; margin: 0;'>🎯 Campaign Performance</h3>", unsafe_allow_html=True)
    with col2:
        if st.button("📈", key="btn_campaign", help="Show Campaign Graph"):
            st.session_state.selected_chart = 'campaign'
            st.rerun()
    
    # Show only top 5 campaigns with key metrics
    display_df = df.head(5)[['campaign', 'impressions', 'ctr']].copy()
    display_df.columns = ['Campaign', 'Impr.', 'CTR']
    
    # Format values (more compact)
    display_df['Impr.'] = display_df['Impr.'].apply(lambda x: f"{x:.0f}")
    display_df['CTR'] = display_df['CTR'].apply(lambda x: f"{x:.1f}%")
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=200
    )
    st.markdown("</div>", unsafe_allow_html=True)

def create_sentiment_distribution_chart(df):
    """Create sentiment distribution pie chart (Improvado style)"""
    sentiment_counts = df['sentiment_label'].value_counts()
    
    fig = go.Figure(data=[go.Pie(
        labels=sentiment_counts.index,
        values=sentiment_counts.values,
        hole=0.5,
        marker=dict(colors=[COLORS['success'], COLORS['danger'], COLORS['neutral']]),
        textinfo='label+percent',
        textposition='outside',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title=dict(
            text="Sentiment Distribution",
            font=dict(size=16, color='#1F2937', family='Arial, sans-serif'),
            x=0,
            xanchor='left'
        ),
        height=350,
        showlegend=True,
        legend=dict(font=dict(size=12)),
        margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor='white',
        font=dict(family='Arial, sans-serif')
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def create_sentiment_timeline(df):
    """Create sentiment trend over time (Improvado style)"""
    df_copy = df.copy()
    df_copy['date'] = pd.to_datetime(df_copy['timestamp']).dt.date
    
    sentiment_by_date = df_copy.groupby(['date', 'sentiment_label']).size().reset_index(name='count')
    
    fig = px.area(
        sentiment_by_date,
        x='date',
        y='count',
        color='sentiment_label',
        title="Sentiment Trend Over Time",
        color_discrete_map={
            'POSITIVE': COLORS['success'],
            'NEGATIVE': COLORS['danger'],
            'NEUTRAL': COLORS['neutral']
        }
    )
    
    fig.update_layout(
        title=dict(
            text="Sentiment Trend Over Time",
            font=dict(size=16, color='#1F2937', family='Arial, sans-serif'),
            x=0,
            xanchor='left'
        ),
        height=350,
        xaxis_title="",
        yaxis_title="Count",
        legend_title="Sentiment",
        margin=dict(l=60, r=40, t=60, b=40),
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(family='Arial, sans-serif')
    )
    
    fig.update_xaxes(showgrid=True, gridcolor='#F3F4F6')
    fig.update_yaxes(showgrid=True, gridcolor='#F3F4F6')
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def create_engagement_sentiment_scatter(df):
    """Create scatter plot of engagement vs sentiment (Improvado style)"""
    fig = px.scatter(
        df,
        x='sentiment_score',
        y='engagement_score',
        color='sentiment_label',
        size='score',
        hover_data=['title', 'subreddit'],
        title="Engagement vs Sentiment Analysis",
        color_discrete_map={
            'POSITIVE': COLORS['success'],
            'NEGATIVE': COLORS['danger'],
            'NEUTRAL': COLORS['neutral']
        }
    )
    
    fig.update_layout(
        title=dict(
            text="Engagement vs Sentiment Analysis",
            font=dict(size=16, color='#1F2937', family='Arial, sans-serif'),
            x=0,
            xanchor='left'
        ),
        height=400,
        xaxis_title="Sentiment Score",
        yaxis_title="Engagement Score",
        legend_title="Sentiment",
        margin=dict(l=60, r=40, t=60, b=60),
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(family='Arial, sans-serif')
    )
    
    fig.update_xaxes(showgrid=True, gridcolor='#F3F4F6')
    fig.update_yaxes(showgrid=True, gridcolor='#F3F4F6')
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def create_subreddit_sentiment_heatmap(df):
    """Create heatmap of sentiment by subreddit (Improvado style)"""
    pivot_data = df.groupby(['subreddit', 'sentiment_label']).size().unstack(fill_value=0)
    
    fig = go.Figure(data=go.Heatmap(
        z=pivot_data.values,
        x=pivot_data.columns,
        y=pivot_data.index,
        colorscale='Purples',
        text=pivot_data.values,
        texttemplate='%{text}',
        textfont={"size": 12},
        hovertemplate='Subreddit: %{y}<br>Sentiment: %{x}<br>Count: %{z}<extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text="Sentiment Distribution by Subreddit",
            font=dict(size=16, color='#1F2937', family='Arial, sans-serif'),
            x=0,
            xanchor='left'
        ),
        height=350,
        xaxis_title="Sentiment",
        yaxis_title="Subreddit",
        margin=dict(l=120, r=40, t=60, b=60),
        paper_bgcolor='white',
        font=dict(family='Arial, sans-serif')
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def display_critical_alerts(df, threshold=0.3):
    """Display critical negative sentiment alerts (Improvado style)"""
    st.markdown("""
    <h3 style='color: #1F2937; font-size: 16px; font-weight: 600; margin: 24px 0 16px 0;'>
        🚨 Critical Alerts
    </h3>
    """, unsafe_allow_html=True)
    
    critical_posts = df[
        (df['sentiment_label'] == 'NEGATIVE') & 
        (df['sentiment_score'] > threshold)
    ].sort_values('sentiment_score', ascending=False)
    
    if len(critical_posts) > 0:
        st.warning(f"⚠️ Found {len(critical_posts)} posts with strong negative sentiment")
        
        for idx, row in critical_posts.head(5).iterrows():
            with st.expander(f"📍 r/{row['subreddit']} - Sentiment Score: {row['sentiment_score']:.3f}"):
                st.markdown(f"**Title:** {row['title']}")
                st.markdown(f"**Engagement:** {row['score']} upvotes | {row['num_comments']} comments")
                if 'permalink' in row:
                    st.markdown(f"**Link:** {row['permalink']}")
    else:
        st.success("✅ No critical negative sentiment detected")

def create_topic_distribution(df):
    """Create topic distribution chart (Improvado style)"""
    if 'topic_label' not in df.columns:
        st.info("Topic modeling data not available")
        return
    
    topic_counts = df['topic_label'].value_counts()
    
    fig = go.Figure(data=[go.Bar(
        x=topic_counts.values,
        y=topic_counts.index,
        orientation='h',
        marker=dict(color=COLORS['primary']),
        hovertemplate='<b>%{y}</b><br>Posts: %{x}<extra></extra>'
    )])
    
    fig.update_layout(
        title=dict(
            text="Discussion Topics Distribution",
            font=dict(size=16, color='#1F2937', family='Arial, sans-serif'),
            x=0,
            xanchor='left'
        ),
        xaxis_title="Number of Posts",
        yaxis_title="",
        height=350,
        margin=dict(l=150, r=40, t=60, b=60),
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(family='Arial, sans-serif')
    )
    
    fig.update_xaxes(showgrid=True, gridcolor='#F3F4F6')
    fig.update_yaxes(showgrid=False)
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

