#!/usr/bin/env python3
"""
FastAPI server for the Intrinsic Value Calculator web application.
Provides REST API endpoints for DCF calculations and company data retrieval.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os
from pathlib import Path
from src.provider import get_info, dcf, calc_up_downside

app = FastAPI(title="Intrinsic Value Calculator API", version="1.0.0")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files from the built React app
static_dir = Path(__file__).parent / "project" / "dist"
if static_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(static_dir / "assets")), name="assets")
    
    @app.get("/")
    async def serve_frontend():
        """Serve the main React app"""
        return FileResponse(str(static_dir / "index.html"))
    
    # Catch-all route for React Router (SPA routing)
    @app.get("/{path:path}")
    async def serve_spa(path: str):
        """Serve React app for all routes (SPA)"""
        # If it's an API route, let it pass through
        if path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        
        # For any other route, serve the React app
        return FileResponse(str(static_dir / "index.html"))

# Pydantic models for request/response validation
class CompanyInfoRequest(BaseModel):
    ticker: str

class HistoricalData(BaseModel):
    revenueGrowth3Y: float
    revenueGrowth2Y: float
    revenueGrowth1Y: float
    dilution3Y: float
    dilution2Y: float
    dilution1Y: float
    fcfMargin3Y: float
    fcfMargin2Y: float
    fcfMargin1Y: float

class CompanyInfoResponse(BaseModel):
    ticker: str
    name: str
    currentPrice: float
    currency: str
    lastYearlyRevenue: float
    totalSharesOut: float
    totalFloatPercent: Optional[float] = None
    totalShortPercent: Optional[float] = None
    averageVolume: Optional[float] = None
    marketCap: Optional[float] = None
    historicalData: HistoricalData

class DCFCalculationRequest(BaseModel):
    ticker: str
    revenueGrowthRate: float
    fcfMargin: float
    numberOfYears: int = 7
    discountRate: float = 10.0
    terminalGrowthRate: float = 6.0

class DCFCalculationResponse(BaseModel):
    fairValue: float
    currentPrice: float
    upsideDownside: float
    yearlyRevenueAfterNYears: float
    requiredRevenueGrowth: float
    requiredFCFMargin: float
    compoundedReturnRate: float

def extract_historical_data(data_string: str) -> HistoricalData:
    """Extract historical data from the tabulated string returned by get_info."""
    lines = data_string.strip().split('\n')
    
    # Initialize with default values
    historical_data = {
        'revenueGrowth3Y': 0.0,
        'revenueGrowth2Y': 0.0,
        'revenueGrowth1Y': 0.0,
        'dilution3Y': 0.0,
        'dilution2Y': 0.0,
        'dilution1Y': 0.0,
        'fcfMargin3Y': 0.0,
        'fcfMargin2Y': 0.0,
        'fcfMargin1Y': 0.0
    }
    
    try:
        # Parse the table data (skip header and separator lines)
        data_lines = []
        for line in lines:
            if line.strip() and not line.startswith('---') and not line.startswith(('Revenue Growth', 'Dilution', 'FCF Margins', 'Analyst')):
                # This is likely a data line, check if it contains the company name
                continue
            elif any(keyword in line for keyword in ['Revenue Growth', 'Dilution', 'FCF Margins']):
                data_lines.append(line)
        
        for line in data_lines:
            parts = line.split()
            if 'Revenue Growth' in line:
                # Extract percentages, handling '-' as 0
                values = [float(p.replace('%', '')) if p.replace('%', '').replace('-', '').replace('.', '').isdigit() and p != '-' else 0.0 
                         for p in parts if '%' in p or p == '-']
                if len(values) >= 3:
                    historical_data['revenueGrowth3Y'] = values[0] if len(values) > 0 else 0.0
                    historical_data['revenueGrowth2Y'] = values[1] if len(values) > 1 else 0.0
                    historical_data['revenueGrowth1Y'] = values[2] if len(values) > 2 else 0.0
            
            elif 'Dilution' in line or 'Buybacks' in line:
                values = [float(p.replace('%', '')) if p.replace('%', '').replace('-', '').replace('.', '').isdigit() and p != '-' else 0.0 
                         for p in parts if '%' in p or p == '-']
                if len(values) >= 3:
                    historical_data['dilution3Y'] = values[0] if len(values) > 0 else 0.0
                    historical_data['dilution2Y'] = values[1] if len(values) > 1 else 0.0
                    historical_data['dilution1Y'] = values[2] if len(values) > 2 else 0.0
            
            elif 'FCF Margins' in line:
                values = [float(p.replace('%', '')) if p.replace('%', '').replace('-', '').replace('.', '').isdigit() and p != '-' else 0.0 
                         for p in parts if '%' in p or p == '-']
                if len(values) >= 3:
                    historical_data['fcfMargin3Y'] = values[0] if len(values) > 0 else 0.0
                    historical_data['fcfMargin2Y'] = values[1] if len(values) > 1 else 0.0
                    historical_data['fcfMargin1Y'] = values[2] if len(values) > 2 else 0.0
    
    except Exception as e:
        print(f"Error parsing historical data: {e}")
    
    return HistoricalData(**historical_data)

@app.get("/")
async def root():
    return {"message": "Intrinsic Value Calculator API", "status": "running"}

@app.post("/api/get_company_info", response_model=CompanyInfoResponse)
async def get_company_info(request: CompanyInfoRequest):
    """Get comprehensive company information and historical data."""
    try:
        # Get data from the existing provider
        current_price, total_shares, prev_rev_growth, starting_rev, prev_fcf_margin, info_data, extra_info = get_info(request.ticker.upper())
        
        # Extract company name from the info_data string (first line contains company name)
        lines = info_data.strip().split('\n')
        company_name = lines[0].split('(')[0].strip() if lines else request.ticker
        
        # Extract currency from the info_data
        currency_match = info_data.split('(')[1].split(')')[0] if '(' in info_data and ')' in info_data else 'USD'
        
        # Parse historical data
        historical_data = extract_historical_data(info_data)
        
        # Check if financials are in USD but stock trades in INR (like INFY)
        financials_in_usd = False
        if isinstance(extra_info, list) and len(extra_info) > 7:
            financial_currency = extra_info[7]  # This is the actual financial currency from yfinance
            # If stock currency is INR but financials are in USD
            if currency_match == "INR" and financial_currency == "USD":
                financials_in_usd = True
        
        # Convert revenue to INR if needed, then to crores
        if financials_in_usd and currency_match == "INR":
            # INFY case: financials in USD, stock price in INR
            usd_to_inr_rate = 83.0  # Current approximate rate
            starting_rev_inr = starting_rev * usd_to_inr_rate
            starting_rev_crores = starting_rev_inr / 10000000  # Convert to crores
        else:
            # Normal case: TCS and others with financials in same currency as stock
            starting_rev_crores = starting_rev / 10000000  # For display in crores
        
        # Convert shares to crores for display
        total_shares_crores = total_shares / 10000000  # Convert to crores for display
        
        # Extract additional info
        market_cap = None
        avg_volume = None
        float_percent = None
        short_percent = None
        
        if len(extra_info) >= 6:
            try:
                # Parse market cap (keep in original units for proper display)
                mcap_str = extra_info[5].replace('$', '').replace('₹', '')
                if 'T' in mcap_str:
                    market_cap = float(mcap_str.replace('T', '')) * 1000000  # Trillions to crores
                elif 'B' in mcap_str:
                    market_cap = float(mcap_str.replace('B', '')) * 10000   # Billions to crores
                elif 'M' in mcap_str:
                    market_cap = float(mcap_str.replace('M', '')) * 10      # Millions to crores
                elif 'K' in mcap_str:
                    market_cap = float(mcap_str.replace('K', '')) * 0.01    # Thousands to crores
                else:
                    # Try to parse raw number and convert to crores
                    market_cap = float(mcap_str) / 10000000  # Raw value to crores
            except Exception as e:
                print(f"Error parsing market cap: {e}, raw value: {extra_info[5] if len(extra_info) > 5 else 'N/A'}")
                market_cap = None
                
            try:
                # Parse float percentage
                if '%' in extra_info[2]:
                    float_percent = float(extra_info[2].replace('%', ''))
            except:
                float_percent = None
                
            try:
                # Parse short percentage  
                if '%' in extra_info[3]:
                    short_percent = float(extra_info[3].replace('%', ''))
            except:
                short_percent = None
                
            try:
                # Parse average volume
                vol_str = extra_info[4].replace('K', '').replace('M', '').replace('B', '')
                if 'K' in extra_info[4]:
                    avg_volume = float(vol_str) * 1000
                elif 'M' in extra_info[4]:
                    avg_volume = float(vol_str) * 1000000
                elif 'B' in extra_info[4]:
                    avg_volume = float(vol_str) * 1000000000
                else:
                    avg_volume = float(vol_str)
            except:
                avg_volume = None
        
        response = CompanyInfoResponse(
            ticker=request.ticker.upper(),
            name=company_name,
            currentPrice=float(current_price),
            currency=currency_match,
            lastYearlyRevenue=float(starting_rev_crores),
            totalSharesOut=float(total_shares_crores),
            totalFloatPercent=float_percent,
            totalShortPercent=short_percent,
            averageVolume=avg_volume,
            marketCap=market_cap,
            historicalData=historical_data
        )
        
        return response
        
    except Exception as e:
        print(f"Error fetching company info: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to fetch company data: {str(e)}")

@app.post("/api/calculate_dcf", response_model=DCFCalculationResponse)
async def calculate_dcf(request: DCFCalculationRequest):
    """Calculate DCF valuation for a company."""
    try:
        # Get company data first
        current_price, total_shares, prev_rev_growth, starting_rev, prev_fcf_margin, info_data, extra_info = get_info(request.ticker.upper())
        
        # Get currency from info_data
        currency_match = info_data.split('(')[1].split(')')[0] if '(' in info_data and ')' in info_data else 'USD'
        
        # Check if financials are in USD but stock trades in INR (like INFY)
        financials_in_usd = False
        if isinstance(extra_info, list) and len(extra_info) > 7:
            financial_currency = extra_info[7]  # This is the actual financial currency from yfinance
            # If stock currency is INR but financials are in USD
            if currency_match == "INR" and financial_currency == "USD":
                financials_in_usd = True
        
        # Convert starting_rev to INR if needed for DCF calculation
        if financials_in_usd and currency_match == "INR":
            # INFY case: financials in USD, stock price in INR
            usd_to_inr_rate = 83.0  # Current approximate rate
            starting_rev_dcf = starting_rev * usd_to_inr_rate
        else:
            # Normal case: TCS and others with financials in same currency as stock
            starting_rev_dcf = starting_rev
        
        # Convert percentages to decimals
        rev_growth_rate = request.revenueGrowthRate / 100.0
        fcf_margin = request.fcfMargin / 100.0
        discount_rate = request.discountRate / 100.0
        terminal_growth_rate = request.terminalGrowthRate / 100.0
        
        # Calculate DCF using converted revenue
        results = dcf(
            rev_growth_rate, 
            fcf_margin, 
            request.numberOfYears, 
            starting_rev_dcf, 
            discount_rate, 
            terminal_growth_rate, 
            total_shares, 
            current_price
        )
        
        fair_value, required_rev_growth, required_discount_rate, required_fcf_margin, assumed_cagr = results
        
        # Calculate projected revenue after N years using converted revenue (convert to crores for display)
        yearly_revenue_after_n_years = (starting_rev_dcf * ((1 + rev_growth_rate) ** request.numberOfYears)) / 10000000
        
        # Calculate upside/downside
        upside_downside = calc_up_downside(fair_value, current_price)
        
        response = DCFCalculationResponse(
            fairValue=float(fair_value),
            currentPrice=float(current_price),
            upsideDownside=float(upside_downside),
            yearlyRevenueAfterNYears=float(yearly_revenue_after_n_years),
            requiredRevenueGrowth=float(required_rev_growth),
            requiredFCFMargin=float(required_fcf_margin),
            compoundedReturnRate=float(required_discount_rate)
        )
        
        return response
        
    except Exception as e:
        print(f"Error calculating DCF: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to calculate DCF: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API server is running"}

if __name__ == "__main__":
    print("Starting Intrinsic Value Calculator API Server...")
    port = int(os.environ.get("PORT", 8000))
    print(f"Server will be available at: http://localhost:{port}")
    print(f"API documentation will be available at: http://localhost:{port}/docs")
    
    # Check if we have built frontend files
    static_dir = Path(__file__).parent / "project" / "dist"
    if static_dir.exists():
        print("✅ Frontend build found - serving full-stack application")
    else:
        print("⚠️  Frontend build not found - API only mode")
    
    uvicorn.run(app, host="0.0.0.0", port=port)