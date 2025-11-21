# 🚀 Improvado Marketing Intelligence PoC

A production-ready data engineering and machine learning proof of concept demonstrating advanced marketing analytics capabilities using Reddit data, NLP sentiment analysis, and interactive dashboards.

## 🎯 Project Overview

This PoC showcases:
- **Data Engineering**: Reddit API → MongoDB (Data Lake) → SQLite (Data Warehouse)
- **Machine Learning**: Sentiment analysis using HuggingFace Transformers
- **Business Intelligence**: Interactive Streamlit dashboard with real-time KPIs
- **Production-Ready Code**: Error handling, logging, modular architecture

## 📊 Features

### Executive Dashboard
- Real-time marketing KPIs (Spend, CPM, CTR, CPC)
- Channel performance analytics (Programmatic, Paid Search, Paid Social, Organic)
- Data source performance tracking
- Campaign performance metrics
- Interactive time-series visualizations

### AI Customer Voice Analysis
- Sentiment analysis of marketing discussions on Reddit
- Topic modeling for trend identification
- Engagement vs sentiment correlation analysis
- Critical alerts for negative sentiment spikes

## 🚀 Quick Start

```bash
# Clone repository
git clone <your-repo-url>
cd improvado-marketing-intelligence

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Generate demo data
python src/etl/generate_kpi_data.py

# Launch dashboard
streamlit run app.py
```
## 📁 Project Structure
improvado-marketing-intelligence/
├── data/                    # Local SQLite storage
├── src/
│   ├── etl/                # ETL scripts
│   ├── ml/                 # NLP models
│   └── dashboard/          # Streamlit components
├── app.py                  # Main entry point
├── requirements.txt
├── .env.example
└── README.md

## 🔑 Key Technologies
* Frontend: Streamlit 1.31
* Databases: MongoDB (Raw), SQLite (Curated)
* ML/NLP: HuggingFace Transformers (DistilBERT)
* Data Processing: Pandas, NumPy
* Visualization: Plotly, Altair
* API: PRAW (Reddit API wrapper)

## 📈 Business Value
* Real-time customer sentiment monitoring for proactive strategy adjustments
* Competitive intelligence from community discussions
* Data-driven marketing decisions with ML-powered insights
* ROI improvement potential of 15-25% through early trend detection

## 📄 License
MIT License - See LICENSE file for details