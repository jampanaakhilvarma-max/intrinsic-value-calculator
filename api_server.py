"""
ValueLab India - DCF Calculator API
Simple, reliable Python backend for Indian stock valuation
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import traceback
import logging
import os
import uvicorn

# Import the existing working backend functions
from src.provider import get_info, dcf

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ValueLab India - DCF Calculator API",
    description="Professional DCF valuation for Indian stocks",
    version="1.0.0"
)

# Add CORS middleware - Allow all origins for now
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class CompanyInfoRequest(BaseModel):
    ticker: str

class DCFCalculationRequest(BaseModel):
    ticker: str
    revenueGrowthRate: float
    fcfMargin: float
    numberOfYears: int = 7
    discountRate: float = 10.0
    terminalGrowthRate: float = 6.0  # Default changed to 6%

# Simple HTML page for the root
HTML_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>ValueLab India - DCF Calculator API</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            margin: 0; 
            padding: 40px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container { 
            max-width: 900px; 
            margin: 0 auto; 
            background: white; 
            padding: 40px; 
            border-radius: 15px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.2); 
        }
        h1 { 
            color: #2c3e50; 
            text-align: center; 
            margin-bottom: 10px; 
            font-size: 2.5em;
        }
        .subtitle {
            text-align: center; 
            color: #7f8c8d; 
            margin-bottom: 40px; 
            font-size: 1.2em;
        }
        .status { 
            background: linear-gradient(45deg, #28a745, #20c997); 
            color: white; 
            padding: 15px; 
            border-radius: 8px; 
            text-align: center; 
            margin: 30px 0; 
            font-weight: bold;
            font-size: 1.1em;
        }
        .endpoint { 
            background: #f8f9fa; 
            padding: 25px; 
            margin: 25px 0; 
            border-radius: 10px; 
            border-left: 5px solid #007bff; 
            transition: transform 0.2s;
        }
        .endpoint:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .method { 
            background: #28a745; 
            color: white; 
            padding: 6px 12px; 
            border-radius: 20px; 
            font-size: 12px; 
            font-weight: bold;
            display: inline-block;
            margin-bottom: 10px;
        }
        .method.post { background: #ffc107; color: #000; }
        pre { 
            background: #2c3e50; 
            color: #ecf0f1; 
            padding: 15px; 
            border-radius: 5px; 
            overflow-x: auto; 
            font-family: 'Monaco', 'Consolas', monospace;
        }
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin: 30px 0;
        }
        .card {
            background: #fff;
            padding: 25px;
            border-radius: 10px;
            border: 1px solid #e9ecef;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .stocks {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
            margin: 20px 0;
        }
        .stock {
            background: #e3f2fd;
            padding: 8px 12px;
            border-radius: 5px;
            font-family: monospace;
            text-align: center;
            font-weight: bold;
        }
        .footer {
            margin-top: 50px;
            padding: 30px;
            background: #2c3e50;
            color: white;
            border-radius: 10px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 ValueLab India</h1>
        <div class="subtitle">Professional DCF Calculator for Indian Stock Market</div>
        <div class="status">✅ API Server is Running Successfully!</div>
        
        <h2>📊 API Endpoints</h2>
        
        <div class="endpoint">
            <span class="method post">POST</span>
            <h3>/api/get_company_info</h3>
            <p><strong>Description:</strong> Get comprehensive company financial data for Indian stocks</p>
            <p><strong>Request Body:</strong></p>
            <pre>{"ticker": "RELIANCE.NS"}</pre>
            <p><strong>Returns:</strong> Current price, market cap, revenue, shares outstanding, and historical growth data</p>
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span>
            <h3>/api/calculate_dcf</h3>
            <p><strong>Description:</strong> Calculate Discounted Cash Flow (DCF) valuation with sensitivity analysis</p>
            <p><strong>Request Body:</strong></p>
            <pre>{
    "ticker": "RELIANCE.NS",
    "revenueGrowthRate": 10.0,
    "fcfMargin": 15.0,
    "numberOfYears": 7,
    "discountRate": 12.0,
    "terminalGrowthRate": 6.0
}</pre>
            <p><strong>Returns:</strong> Fair value, upside/downside %, required metrics for target returns</p>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>🏛️ Supported Exchanges</h3>
                <ul>
                    <li><strong>NSE:</strong> Add .NS suffix (e.g., RELIANCE.NS)</li>
                    <li><strong>BSE:</strong> Add .BO suffix (e.g., 500325.BO)</li>
                </ul>
            </div>
            <div class="card">
                <h3>💡 Key Features</h3>
                <ul>
                    <li>Real-time stock data via yfinance</li>
                    <li>Hardcoded currency conversion factor = 1</li>
                    <li>Terminal Growth Rate default = 6%</li>
                    <li>Comprehensive Indian stock coverage</li>
                </ul>
            </div>
        </div>
        
        <h3>🔥 Popular Indian Stocks</h3>
        <div class="stocks">
            <div class="stock">RELIANCE.NS</div>
            <div class="stock">TCS.NS</div>
            <div class="stock">HDFCBANK.NS</div>
            <div class="stock">INFY.NS</div>
            <div class="stock">ICICIBANK.NS</div>
            <div class="stock">HINDUNILVR.NS</div>
            <div class="stock">SBIN.NS</div>
            <div class="stock">BHARTIARTL.NS</div>
            <div class="stock">ITC.NS</div>
            <div class="stock">KOTAKBANK.NS</div>
            <div class="stock">LT.NS</div>
            <div class="stock">AXISBANK.NS</div>
        </div>
        
        <div class="footer">
            <h3>🔧 ValueLab India v1.0.0</h3>
            <p><strong>Built for:</strong> Professional Indian stock valuation and analysis</p>
            <p><strong>Technology:</strong> FastAPI + Python + yfinance</p>
            <p><strong>Status:</strong> Production Ready ✨</p>
        </div>
    </div>
</body>
</html>
"""

def format_number_for_display(value, currency):
    """Format large numbers for display (Crores/Lakhs for INR, Millions/Billions for USD)"""
    try:
        if currency == "INR":
            if value >= 10000000:  # 1 crore
                return f"{value/10000000:.2f}"
            elif value >= 100000:  # 1 lakh
                return f"{value/100000:.2f}"
            else:
                return f"{value:.2f}"
        else:  # USD and others
            if value >= 1000000000:  # 1 billion
                return f"{value/1000000000:.2f}"
            elif value >= 1000000:  # 1 million
                return f"{value/1000000:.2f}"
            else:
                return f"{value:.2f}"
    except (TypeError, ValueError):
        return str(value)

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the API documentation page"""
    return HTMLResponse(content=HTML_CONTENT)

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    return {"status": "healthy", "message": "ValueLab India API is running", "version": "1.0.0"}

@app.post("/api/get_company_info")
async def get_company_info_endpoint(request: CompanyInfoRequest):
    """Get company information for DCF calculation"""
    try:
        logger.info(f"Getting company info for {request.ticker}")
        
        # Call the existing backend function
        result = get_info(request.ticker)
        
        if not result or len(result) < 6:
            raise HTTPException(status_code=404, detail=f"No data found for ticker {request.ticker}")
        
        # Parse the result tuple
        current_price, yearly_revenue, shares_outstanding, market_cap, currency, info_str = result
        
        # Parse historical data from info_str
        lines = info_str.split('\n') if info_str else []
        
        # Initialize historical data
        historical_data = {
            "revenueGrowth3Y": 0.0,
            "revenueGrowth2Y": 0.0, 
            "revenueGrowth1Y": 0.0,
            "dilution3Y": 0.0,
            "dilution2Y": 0.0,
            "dilution1Y": 0.0,
            "fcfMargin3Y": 0.0,
            "fcfMargin2Y": 0.0,
            "fcfMargin1Y": 0.0
        }
        
        # Parse revenue growth rates
        for line in lines:
            if 'Revenue Growth' in line:
                parts = line.split()
                percentages = []
                for part in parts:
                    if '%' in part:
                        try:
                            percentages.append(float(part.replace('%', '')))
                        except ValueError:
                            continue
                
                if len(percentages) >= 3:
                    historical_data["revenueGrowth3Y"] = percentages[0] if len(percentages) > 0 else 0.0
                    historical_data["revenueGrowth2Y"] = percentages[1] if len(percentages) > 1 else 0.0
                    historical_data["revenueGrowth1Y"] = percentages[2] if len(percentages) > 2 else 0.0
        
        # Format numbers for display
        formatted_yearly_revenue = format_number_for_display(yearly_revenue, currency)
        formatted_market_cap = format_number_for_display(market_cap, currency)
        
        company_data = {
            "ticker": request.ticker,
            "name": request.ticker.replace('.NS', '').replace('.BO', ''),  # Simple name extraction
            "currentPrice": current_price,
            "lastYearlyRevenue": formatted_yearly_revenue,
            "totalSharesOut": shares_outstanding,
            "marketCap": formatted_market_cap,
            "currency": currency,
            "historicalData": historical_data
        }
        
        logger.info(f"Successfully retrieved data for {request.ticker}")
        return company_data
        
    except Exception as e:
        logger.error(f"Error getting company info for {request.ticker}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=f"Failed to get company info: {str(e)}")

@app.post("/api/calculate_dcf")
async def calculate_dcf_endpoint(request: DCFCalculationRequest):
    """Calculate DCF valuation"""
    try:
        logger.info(f"Calculating DCF for {request.ticker}")
        
        # Get basic company info first
        info_result = get_info(request.ticker)
        if not info_result or len(info_result) < 6:
            raise HTTPException(status_code=404, detail=f"No data found for ticker {request.ticker}")
        
        current_price, starting_rev, total_shares, market_cap, currency, info_str = info_result
        
        # Call the existing DCF function
        results = dcf(
            ticker=request.ticker,
            starting_rev=starting_rev,
            rg=request.revenueGrowthRate / 100,    # Convert percentage to decimal
            years=request.numberOfYears,
            fcf_margin=request.fcfMargin / 100,    # Convert percentage to decimal
            dr=request.discountRate / 100,         # Convert percentage to decimal
            tgr=request.terminalGrowthRate / 100,  # Convert percentage to decimal
            total_shares=total_shares,
            current_price=current_price
        )
        
        # Unpack results
        fair_value, required_revenue_growth, required_wacc, required_fcf_margin, assumed_cagr = results
        
        # Calculate additional metrics
        upside_downside = ((fair_value - current_price) / current_price) * 100
        yearly_revenue_after_n = starting_rev * ((1 + request.revenueGrowthRate/100) ** request.numberOfYears)
        
        # Format the yearly revenue for display
        formatted_yearly_revenue = format_number_for_display(yearly_revenue_after_n, currency)
        
        dcf_results = {
            "fairValue": fair_value,
            "currentPrice": current_price,
            "upsideDownside": upside_downside,
            "yearlyRevenueAfterNYears": formatted_yearly_revenue,
            "requiredRevenueGrowth": required_revenue_growth,
            "requiredFCFMargin": required_fcf_margin,
            "compoundedReturnRate": assumed_cagr
        }
        
        logger.info(f"Successfully calculated DCF for {request.ticker}")
        return dcf_results
        
    except Exception as e:
        logger.error(f"Error calculating DCF for {request.ticker}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=f"Failed to calculate DCF: {str(e)}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("api_server:app", host="0.0.0.0", port=port)