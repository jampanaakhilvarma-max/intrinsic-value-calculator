
# Intrinsic Value Calculator 📊

Professional DCF (Discounted Cash Flow) stock valuation calculator built for Indian markets with modern web interface.

## 🌟 Features

- **Professional DCF Analysis** - Warren Buffett style intrinsic value calculation
- **Indian Stock Market Focus** - Optimized for NSE stocks with INR currency support  
- **Currency Conversion** - Automatic USD to INR conversion for mixed-currency stocks (like INFY)
- **Real-time Data** - Live stock data via Yahoo Finance API
- **Modern Web Interface** - React frontend with dark/light mode
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Batch Processing** - Analyze multiple stocks from CSV files
- **RESTful API** - FastAPI backend for programmatic access

## 🚀 Live Demo

🌐 **[Try the Live Application](https://intrinsic-value-calculator-production.up.railway.app)**

## 🏗️ Architecture

- **Backend**: FastAPI (Python)
- **Frontend**: React + TypeScript + Tailwind CSS  
- **Data Source**: Yahoo Finance API
- **Deployment**: Railway Platform
- **Currency Support**: INR, USD with automatic conversion

## 🛠️ Local Development

### Prerequisites
- Python 3.9+
- Node.js 18+

### Quick Start
```bash
# Clone and setup
git clone https://github.com/jampanaakhilvarma-max/intrinsic-value-calculator.git
cd intrinsic-value-calculator

# Install dependencies
pip install -r requirements.txt

# Build frontend and start server
bash start.sh
```

Visit `http://localhost:8000` for the web interface.

## 🎯 Usage

### Web Interface
1. Search for Indian stocks (e.g., "TCS", "INFY", "RELIANCE")
2. Review company data and historical metrics
3. Adjust DCF parameters based on your analysis
4. Get fair value calculation with upside/downside analysis

### Command Line  
```bash
# Quick analysis
python get_fair_value.py TCS.NS 15 20

# Batch analysis
python batch_mode.py batch_mode_files/example.csv
```

### API Usage
```bash
# Get company info
curl -X POST "http://localhost:8000/api/get_company_info" \
  -H "Content-Type: application/json" \
  -d '{"ticker": "TCS.NS"}'
```

## 💰 Currency Handling

- **INR-only stocks** (TCS.NS): Direct INR calculations
- **Mixed currency stocks** (INFY.NS): USD financials → INR conversion  
- **Display**: All results in Indian Rupees (₹) and Crores

## ⚠️ Disclaimer

This tool is for educational purposes. Always conduct your own research before making investment decisions.
