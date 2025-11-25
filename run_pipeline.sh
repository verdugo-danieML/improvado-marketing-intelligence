#!/bin/bash

echo "🚀 Starting ETL Pipeline..."

# 1. Extract Data
echo "-----------------------------------"
echo "📥 Extracting YouTube comments..."
python3 src/etl/extract_youtube.py

# 2. Process Data
echo "-----------------------------------"
echo "🔄 Processing data..."
python3 src/etl/process_youtube_data.py

# 3. Analyze Sentiment
echo "-----------------------------------"
echo "🧠 Analyzing sentiment..."
python3 src/ml/sentiment_analysis.py

# 4. Load to Database
echo "-----------------------------------"
echo "💾 Loading to SQLite..."
python3 src/etl/load_to_sqlite.py

echo "-----------------------------------"
echo "✅ Pipeline Complete!"
echo "Run 'streamlit run app.py' to view the dashboard."