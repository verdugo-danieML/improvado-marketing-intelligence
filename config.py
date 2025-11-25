"""
Configuration Management Module
Centralizes all configuration settings and environment variables
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()

# Project Root
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
SRC_DIR = PROJECT_ROOT / "src"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

# SQLite Configuration
SQLITE_CONFIG = {
    "db_path": os.getenv("SQLITE_DB_PATH", str(DATA_DIR / "improvado_data.db")),
}

# Application Settings
APP_CONFIG = {
    "log_level": os.getenv("LOG_LEVEL", "INFO"),
    "batch_size": int(os.getenv("BATCH_SIZE", "32")),
}

# ML Model Configuration
ML_CONFIG = {
    "sentiment_model": "distilbert-base-uncased-finetuned-sst-2-english",
    "device": "cpu",  # Change to "cuda" if GPU available
    "max_length": 512,
    "batch_size": 16,
}

# Dashboard KPI Values (from reference image)
DASHBOARD_KPI_TARGETS = {
    "spend": {"value": 36.00, "unit": "M", "change": 491.79, "change_unit": "K"},
    "cpm": {"value": 405, "unit": "K", "change": 1.28, "change_unit": "K"},
    "ctr": {"value": 10.5, "unit": "%", "change": 0.08, "change_unit": "%"},
    "cpc": {"value": 4, "unit": "K", "change": -18.34, "change_unit": ""},
    "video_views": {"value": 93, "unit": "K", "change": 993.0, "change_unit": ""},
    "impressions": {"value": 89.0, "unit": "K", "change": 937.0, "change_unit": ""},
    "conversions": {"value": 791, "unit": "", "change": 36.0, "change_unit": ""},
    "conversion_rate": {"value": 9.8, "unit": "%", "change": 0.27, "change_unit": "%"},
}

# Channel Performance Data (from reference image)
CHANNEL_PERFORMANCE = {
    "Programmatic": {"impressions": 54.7, "ctr": 10.44, "spend_pct": 4.2},
    "Paid Search": {"impressions": 31.4, "ctr": 10.57, "spend_pct": 30.7},
    "Paid Social": {"impressions": 2.9, "ctr": 10.28, "spend_pct": -25.6},
    "Organic": {"impressions": 11.5, "ctr": 10.6, "spend_pct": -0.6},
}

# Logging Configuration
logger.remove()  # Remove default handler
logger.add(
    "logs/app_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="7 days",
    level=APP_CONFIG["log_level"],
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)
logger.add(lambda msg: print(msg, end=""), level="INFO")  # Console output

# Validate critical configurations
def validate_config():
    """Validate that critical configurations are set"""
    warnings = []
    
    if not os.getenv("YOUTUBE_API_KEY"):
        warnings.append("⚠️  YOUTUBE_API_KEY not set in .env")
    
    if warnings:
        logger.warning("Configuration warnings:")
        for warning in warnings:
            logger.warning(f"  {warning}")
        logger.info("  → Application will use fallback/dummy data mode")
    else:
        logger.success("✓ All critical configurations validated")

if __name__ == "__main__":
    validate_config()
    logger.info(f"Project Root: {PROJECT_ROOT}")
    logger.info(f"Data Directory: {DATA_DIR}")
    logger.info(f"SQLite Database: {SQLITE_CONFIG['db_path']}")