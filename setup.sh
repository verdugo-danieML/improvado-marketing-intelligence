#!/bin/bash

# Improvado Marketing Intelligence PoC - Setup Script
# This script automates the initial setup process

echo "🚀 Improvado Marketing Intelligence PoC - Setup"
echo "================================================"
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python is installed
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.9 or higher.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓ Found Python ${PYTHON_VERSION}${NC}"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠ Virtual environment already exists${NC}"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet
echo -e "${GREEN}✓ Pip upgraded${NC}"
echo ""

# Install dependencies
echo "Installing dependencies (this may take a few minutes)..."
pip install -r requirements.txt --quiet
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ All dependencies installed${NC}"
else
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    exit 1
fi
echo ""

# Create data directories
echo "Creating data directories..."
mkdir -p data
mkdir -p data/raw_json
mkdir -p logs
echo -e "${GREEN}✓ Directories created${NC}"
echo ""

# Copy .env.example to .env if not exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo -e "${GREEN}✓ .env file created${NC}"
    echo -e "${YELLOW}⚠ Please edit .env and add your API credentials${NC}"
else
    echo -e "${YELLOW}⚠ .env file already exists${NC}"
fi
echo ""

# Validate configuration
echo "Validating configuration..."
python3 config.py
echo ""

# Generate initial data
echo "Generating initial KPI data for dashboard..."
python3 src/etl/generate_kpi_data.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ KPI data generated successfully${NC}"
else
    echo -e "${RED}❌ Failed to generate KPI data${NC}"
fi
echo ""

# Setup complete
echo "================================================"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Reddit API credentials"
echo "2. Run the dashboard: streamlit run app.py"
echo "3. Or run the full pipeline:"
echo "   - python src/etl/extract_reddit.py"
echo "   - python src/etl/process_data.py"
echo "   - python src/ml/sentiment_analysis.py"
echo "   - python src/etl/load_to_sqlite.py"
echo ""
echo "For more information, see README.md"
echo "================================================"