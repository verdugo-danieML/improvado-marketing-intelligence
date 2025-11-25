"""
Generate KPI Data for Dashboard
Creates intelligent dummy data matching the reference dashboard exactly
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from config import SQLITE_CONFIG, DASHBOARD_KPI_TARGETS, CHANNEL_PERFORMANCE, logger

def create_database_schema(conn):
    """Create necessary tables in SQLite database"""
    cursor = conn.cursor()
    
    # Marketing KPIs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS marketing_kpis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            metric_name TEXT NOT NULL,
            metric_value REAL NOT NULL,
            metric_unit TEXT,
            change_value REAL,
            change_unit TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Channel Performance table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS channel_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            channel TEXT NOT NULL,
            impressions REAL NOT NULL,
            ctr REAL NOT NULL,
            spend_pct REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Data Source Performance table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS data_source_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            source TEXT NOT NULL,
            impressions REAL NOT NULL,
            spend_pct REAL,
            ctr REAL NOT NULL,
            conversions_pct REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Campaign Performance table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS campaign_performance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            campaign TEXT NOT NULL,
            impressions INTEGER NOT NULL,
            spend_pct REAL,
            ctr REAL NOT NULL,
            conversions_pct REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Time series data for charts
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS time_series_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            channel TEXT NOT NULL,
            value REAL NOT NULL,
            metric_type TEXT DEFAULT 'impressions',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    logger.info("✓ Database schema created successfully")

def generate_kpi_data(conn):
    """Generate main KPI metrics matching dashboard targets"""
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute("DELETE FROM marketing_kpis")
    
    today = datetime.now().date()
    
    kpis = [
        ('spend', DASHBOARD_KPI_TARGETS['spend']['value'], 
         DASHBOARD_KPI_TARGETS['spend']['unit'], 
         DASHBOARD_KPI_TARGETS['spend']['change'], 
         DASHBOARD_KPI_TARGETS['spend']['change_unit']),
        
        ('cpm', DASHBOARD_KPI_TARGETS['cpm']['value'], 
         DASHBOARD_KPI_TARGETS['cpm']['unit'], 
         DASHBOARD_KPI_TARGETS['cpm']['change'], 
         DASHBOARD_KPI_TARGETS['cpm']['change_unit']),
        
        ('ctr', DASHBOARD_KPI_TARGETS['ctr']['value'], 
         DASHBOARD_KPI_TARGETS['ctr']['unit'], 
         DASHBOARD_KPI_TARGETS['ctr']['change'], 
         DASHBOARD_KPI_TARGETS['ctr']['change_unit']),
        
        ('cpc', DASHBOARD_KPI_TARGETS['cpc']['value'], 
         DASHBOARD_KPI_TARGETS['cpc']['unit'], 
         DASHBOARD_KPI_TARGETS['cpc']['change'], 
         DASHBOARD_KPI_TARGETS['cpc']['change_unit']),
        
        ('video_views', DASHBOARD_KPI_TARGETS['video_views']['value'], 
         DASHBOARD_KPI_TARGETS['video_views']['unit'], 
         DASHBOARD_KPI_TARGETS['video_views']['change'], 
         DASHBOARD_KPI_TARGETS['video_views']['change_unit']),
        
        ('impressions', DASHBOARD_KPI_TARGETS['impressions']['value'], 
         DASHBOARD_KPI_TARGETS['impressions']['unit'], 
         DASHBOARD_KPI_TARGETS['impressions']['change'], 
         DASHBOARD_KPI_TARGETS['impressions']['change_unit']),
        
        ('conversions', DASHBOARD_KPI_TARGETS['conversions']['value'], 
         DASHBOARD_KPI_TARGETS['conversions']['unit'], 
         DASHBOARD_KPI_TARGETS['conversions']['change'], 
         DASHBOARD_KPI_TARGETS['conversions']['change_unit']),
        
        ('conversion_rate', DASHBOARD_KPI_TARGETS['conversion_rate']['value'], 
         DASHBOARD_KPI_TARGETS['conversion_rate']['unit'], 
         DASHBOARD_KPI_TARGETS['conversion_rate']['change'], 
         DASHBOARD_KPI_TARGETS['conversion_rate']['change_unit']),
    ]
    
    cursor.executemany("""
        INSERT INTO marketing_kpis (date, metric_name, metric_value, metric_unit, change_value, change_unit)
        VALUES (?, ?, ?, ?, ?, ?)
    """, [(today, *kpi) for kpi in kpis])
    
    conn.commit()
    logger.info(f"✓ Generated {len(kpis)} KPI metrics")

def generate_channel_performance(conn):
    """Generate channel performance data"""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM channel_performance")
    
    today = datetime.now().date()
    
    channels = []
    for channel_name, data in CHANNEL_PERFORMANCE.items():
        channels.append((
            today,
            channel_name,
            data['impressions'],
            data['ctr'],
            data['spend_pct']
        ))
    
    cursor.executemany("""
        INSERT INTO channel_performance (date, channel, impressions, ctr, spend_pct)
        VALUES (?, ?, ?, ?, ?)
    """, channels)
    
    conn.commit()
    logger.info(f"✓ Generated {len(channels)} channel performance records")

def generate_data_source_performance(conn):
    """Generate data source performance data"""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM data_source_performance")
    
    # Generate data for Jan 2023 - Dec 2023 (12 months)
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(days=30*i) for i in range(12)]
    
    # Data from reference image (base values)
    data_sources = [
        ('Amazon Ad Server (Sizmek)', 5.8, -30.0, 10.17, -10.0),
        ('StackAdapt', 4.8, None, 68.7, -7.3),
        ('LinkedIn Ads', 9.8, None, 10.0, None),
        ('Facebook', 5.7, 39.0, 10.82, 14.3),
        ('Google Display & Video 360', 4.7, 69.2, 10.28, -0.8),
        ('Bing Ads (Microsoft Advertising)', 4.8, 3.7, 10, -1.8),
        ('Google Search Ads 360', 5.8, -23.6, 10.57, 11.0),
    ]
    
    records = []
    import random
    
    for date in dates:
        for ds in data_sources:
            # Add some random variation to impressions for the time series
            base_impressions = ds[1]
            variation = random.uniform(0.8, 1.2)
            impressions = base_impressions * variation
            
            records.append((
                date.date(),
                ds[0],
                impressions,
                ds[2],
                ds[3],
                ds[4]
            ))
    
    cursor.executemany("""
        INSERT INTO data_source_performance (date, source, impressions, spend_pct, ctr, conversions_pct)
        VALUES (?, ?, ?, ?, ?, ?)
    """, records)
    
    conn.commit()
    logger.info(f"✓ Generated {len(records)} data source records")

def generate_campaign_performance(conn):
    """Generate campaign performance data"""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM campaign_performance")
    
    # Generate data for Jan 2023 - Dec 2023 (12 months)
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(days=30*i) for i in range(12)]
    
    # Campaigns from reference image (base values)
    campaigns = [
        ('Business-focused zero tolerance architecture', 931, None, 10.42, None),
        ('Persistent 24/7 attitude', 914, None, 9.71, None),
        ('Integrated dedicated contingency', 950, None, 9.98, None),
        ('Profound intangible policy', 978, None, 8.69, None),
        ('Centralized modular throughput', 955, None, 9.42, None),
        ('Automated uniform software', 952, None, 10.19, None),
        ('Cross-platform static hierarchy', 946, None, 9.5, None),
        ('Networked value-added time-frame', 953, None, 11.54, None),
    ]
    
    records = []
    import random
    
    for date in dates:
        for camp in campaigns:
            # Add some random variation
            base_impressions = camp[1]
            variation = random.uniform(0.9, 1.1)
            impressions = int(base_impressions * variation)
            
            records.append((
                date.date(),
                camp[0],
                impressions,
                camp[2],
                camp[3],
                camp[4]
            ))
    
    cursor.executemany("""
        INSERT INTO campaign_performance (date, campaign, impressions, spend_pct, ctr, conversions_pct)
        VALUES (?, ?, ?, ?, ?, ?)
    """, records)
    
    conn.commit()
    logger.info(f"✓ Generated {len(records)} campaign records")

def generate_time_series_data(conn):
    """Generate time series data for line chart"""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM time_series_data")
    
    # Generate data for Jan 2023 - Dec 2023 (12 months)
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(days=30*i) for i in range(12)]
    
    channels = ['Programmatic', 'Paid Search', 'Paid Social', 'Organic']
    
    # Base patterns for each channel (in thousands)
    patterns = {
        'Programmatic': [7, 5.5, 8, 10, 7.5, 6, 5.5, 7.5, 12.5, 6, 8, 7],
        'Paid Search': [6, 5, 7.5, 9.5, 6.5, 5.5, 4.5, 6.5, 11.5, 5, 7.5, 6.5],
        'Paid Social': [3, 2.5, 3.5, 4, 3.5, 3, 2.5, 3.5, 5, 2.5, 3, 2.5],
        'Organic': [4, 3.5, 4.5, 5, 4, 3.5, 3, 4, 6, 3.5, 4.5, 4],
    }
    
    records = []
    for channel in channels:
        for i, date in enumerate(dates):
            value = patterns[channel][i]
            records.append((date.date(), channel, value, 'impressions'))
    
    cursor.executemany("""
        INSERT INTO time_series_data (date, channel, value, metric_type)
        VALUES (?, ?, ?, ?)
    """, records)
    
    conn.commit()
    logger.info(f"✓ Generated {len(records)} time series data points")

def main():
    """Main execution function"""
    logger.info("Starting KPI data generation...")
    
    # Create data directory if not exists
    db_path = Path(SQLITE_CONFIG['db_path'])
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Connect to SQLite
    conn = sqlite3.connect(SQLITE_CONFIG['db_path'])
    
    try:
        # Create schema
        create_database_schema(conn)
        
        # Generate all data
        generate_kpi_data(conn)
        generate_channel_performance(conn)
        generate_data_source_performance(conn)
        generate_campaign_performance(conn)
        generate_time_series_data(conn)
        
        logger.success("✅ All KPI data generated successfully!")
        logger.info(f"📁 Database location: {SQLITE_CONFIG['db_path']}")
        
    except Exception as e:
        logger.error(f"❌ Error generating data: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    main()