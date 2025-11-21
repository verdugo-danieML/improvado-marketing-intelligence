#!/bin/bash

# Improvado Marketing Intelligence PoC - Full Pipeline Runner
# This script runs the complete data pipeline from extraction to dashboard

echo "🚀 Running Improvado Marketing Intelligence Pipeline"
echo "====================================================="
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo -e "${GREEN}✓ Virtual environment activated${NC}"
else
    echo -e "${YELLOW}⚠ No virtual environment found. Using system Python${NC}"
fi
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    echo "Please copy .env.example to .env and configure your credentials"
    exit 1
fi

# Step 1: Extract Reddit data
echo -e "${BLUE}Step 1/5: Extracting data from Reddit...${NC}"
python3 src/etl/extract_reddit.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Data extraction complete${NC}"
else
    echo -e "${YELLOW}⚠ Data extraction had issues (may be running in demo mode)${NC}"
fi
echo ""

# Step 2: Process data
echo -e "${BLUE}Step 2/5: Processing and cleaning data...${NC}"
python3 src/etl/process_data.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Data processing complete${NC}"
else
    echo -e "${RED}❌ Data processing failed${NC}"
    exit 1
fi
echo ""

# Step 3: Sentiment analysis
echo -e "${BLUE}Step 3/5: Running sentiment analysis (ML)...${NC}"
echo "This may take a few minutes..."
python3 src/ml/sentiment_analysis.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Sentiment analysis complete${NC}"
else
    echo -e "${RED}❌ Sentiment analysis failed${NC}"
    exit 1
fi
echo ""

# Step 4: Load to SQLite
echo -e "${BLUE}Step 4/5: Loading data to SQLite...${NC}"
python3 src/etl/load_to_sqlite.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Data loaded to database${NC}"
else
    echo -e "${RED}❌ Database loading failed${NC}"
    exit 1
fi
echo ""

# Step 5: Launch dashboard
echo -e "${BLUE}Step 5/5: Launching dashboard...${NC}"
echo ""
echo "====================================================="
echo -e "${GREEN}✅ Pipeline Complete!${NC}"
echo "====================================================="
echo ""
echo "Dashboard will open in your browser..."
echo "If it doesn't open automatically, go to: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the dashboard"
echo ""

streamlit run app.py