"""
FastAPI Backend Server for DCF Calculator
Wraps the existing DCF calculation functions without modifying the core backend code.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
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
    title="DCF Calculator API",
    description="Backend API for Intrinsic Value Calculator using DCF model",
    version="1.0.0"
)

# Add CORS middleware to allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "https://*.railway.app",
        "https://*.up.railway.app",
        "*"  # Allow all origins for deployment (you can restrict this later)
    ],
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
    terminalGrowthRate: float = 2.5

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

class CompanyData(BaseModel):
    ticker: str
    name: str
    lastYearlyRevenue: float
    totalSharesOut: float
    totalFloatPercent: Optional[float]
    totalShortPercent: Optional[float]
    averageVolume: Optional[float]
    marketCap: Optional[float]
    currentPrice: float
    currency: str
    historicalData: HistoricalData

class DCFResults(BaseModel):
    fairValue: float
    currentPrice: float
    upsideDownside: float
    yearlyRevenueAfterNYears: float
    requiredRevenueGrowth: float
    requiredFCFMargin: float
    compoundedReturnRate: float

def parse_percentage_string(value: str) -> float:
    """Parse percentage strings like '5.73%' to float 5.73"""
    if isinstance(value, str) and value.endswith('%'):
        try:
            return float(value[:-1])
        except:
            return 0.0
    elif isinstance(value, (int, float)):
        return float(value)
    else:
        return 0.0

def parse_number_string(value: str) -> float:
    """Parse number strings with K/M/B suffixes"""
    if isinstance(value, str):
        value = value.replace('$', '').replace('₹', '').replace(',', '')
        if value.endswith('K'):
            return float(value[:-1]) * 1000
        elif value.endswith('M'):
            return float(value[:-1]) * 1000000
        elif value.endswith('B'):
            return float(value[:-1]) * 1000000000
        elif value.endswith('T'):
            return float(value[:-1]) * 1000000000000
        else:
            try:
                return float(value)
            except:
                return 0.0
    elif isinstance(value, (int, float)):
        return float(value)
    else:
        return 0.0

def format_number_for_display(value: float, currency: str = "USD") -> float:
    """Format large numbers appropriately for frontend display"""
    if value == 0.0:
        return 0.0
    
    # For Indian stocks, convert to crores (1 crore = 10 million)
    if currency == "INR":
        if value >= 10000000:  # 1 crore
            return value / 10000000  # Return in crores
    
    # For USD stocks, convert to billions if large enough
    elif currency == "USD":
        if value >= 1000000000:  # 1 billion
            return value / 1000000000  # Return in billions
        elif value >= 1000000:  # 1 million
            return value / 1000000  # Return in millions
    
    return value

@app.get("/")
async def root():
    return {"message": "DCF Calculator API is running!", "version": "1.0.0"}

@app.post("/api/get_company_info", response_model=CompanyData)
async def get_company_info(request: CompanyInfoRequest):
    """
    Fetch company information using the existing get_info function
    """
    try:
        logger.info(f"Fetching company info for ticker: {request.ticker}")
        
        # Call the existing backend function - handle any errors gracefully
        try:
            current_price, total_shares, prev_rev_growth, starting_rev, prev_fcf_margin, info_str, extra_info = get_info(request.ticker.upper())
        except Exception as backend_error:
            logger.error(f"Backend error for {request.ticker}: {str(backend_error)}")
            # Return minimal data structure if backend fails
            return CompanyData(
                ticker=request.ticker.upper(),
                name=f"{request.ticker.upper()} (Data Error)",
                lastYearlyRevenue=0.0,
                totalSharesOut=0.0,
                totalFloatPercent=None,
                totalShortPercent=None,
                averageVolume=None,
                marketCap=None,
                currentPrice=0.0,
                currency="USD",
                historicalData=HistoricalData(
                    revenueGrowth3Y=0.0,
                    revenueGrowth2Y=0.0,
                    revenueGrowth1Y=0.0,
                    dilution3Y=0.0,
                    dilution2Y=0.0,
                    dilution1Y=0.0,
                    fcfMargin3Y=0.0,
                    fcfMargin2Y=0.0,
                    fcfMargin1Y=0.0
                )
            )
        
        # Parse the tabulated info string to extract historical data
        # The info_str contains a table format - we need to extract specific rows
        
        def parse_table_data(info_str: str) -> tuple:
            """Parse the tabulated data to extract historical percentages"""
            # Split the entire string and find percentage values
            parts = info_str.split()
            percentages = []
            for part in parts:
                if '%' in part and part != '%':
                    try:
                        percentages.append(float(part.replace('%', '')))
                    except:
                        pass
            
            # The format is: Rev Growth (3Y, 2Y, 1Y), Dilution (3Y, 2Y, 1Y), FCF Margins (3Y, 2Y, 1Y)
            # Based on our test data: [5.73, 2.88, 3.85, -0.53, -0.43, 0.18, 13.91, 15.53, 21.21]
            
            if len(percentages) >= 9:
                return (
                    [percentages[0], percentages[1], percentages[2]],  # Revenue Growth
                    [percentages[3], percentages[4], percentages[5]],  # Dilution
                    [percentages[6], percentages[7], percentages[8]]   # FCF Margins
                )
            else:
                # Fallback to the actual backend values if parsing fails
                return (
                    [prev_rev_growth * 100, prev_rev_growth * 100, prev_rev_growth * 100],  # Use actual backend value
                    [0.0, 0.0, 0.0],  # Default dilution
                    [prev_fcf_margin * 100, prev_fcf_margin * 100, prev_fcf_margin * 100]  # Use actual backend value
                )
        
        rev_growth_values, dilution_values, fcf_margin_values = parse_table_data(info_str)
        
        # Parse extra_info: ['$revenue', 'shares', 'float%', 'short%', 'avgVol', 'mcap', conversion_factor]
        revenue_str = extra_info[0] if len(extra_info) > 0 else '0'
        shares_str = extra_info[1] if len(extra_info) > 1 else '0'
        float_percent_str = extra_info[2] if len(extra_info) > 2 else '0%'
        short_percent_str = extra_info[3] if len(extra_info) > 3 else '0%'
        avg_vol_str = extra_info[4] if len(extra_info) > 4 else '0'
        mcap_str = extra_info[5] if len(extra_info) > 5 else '0'
        
        # Convert values
        revenue_value = parse_number_string(revenue_str)
        shares_value = parse_number_string(shares_str)
        float_percent = parse_percentage_string(float_percent_str) if float_percent_str != '-' else None
        short_percent = parse_percentage_string(short_percent_str) if short_percent_str != '-' else None
        avg_volume = parse_number_string(avg_vol_str) if avg_vol_str != '-' else None
        market_cap = parse_number_string(mcap_str) if mcap_str != '-' else None
        
        # Extract company name from info_str first line
        lines = info_str.split('\n')
        first_line = lines[0] if lines else f"{request.ticker} Company"
        company_name = first_line.split('(')[0].strip()
        
        # Determine currency
        currency = "INR" if ".NS" in request.ticker.upper() else "USD"
        
        # Format large numbers for proper display
        formatted_revenue = format_number_for_display(revenue_value, currency)
        formatted_shares = format_number_for_display(shares_value, currency)
        formatted_market_cap = format_number_for_display(market_cap, currency) if market_cap else None
        formatted_avg_volume = format_number_for_display(avg_volume, currency) if avg_volume else None
        
        # Build response
        company_data = CompanyData(
            ticker=request.ticker.upper(),
            name=company_name,
            lastYearlyRevenue=formatted_revenue,
            totalSharesOut=formatted_shares,
            totalFloatPercent=float_percent,
            totalShortPercent=short_percent,
            averageVolume=formatted_avg_volume,
            marketCap=formatted_market_cap,
            currentPrice=current_price,
            currency=currency,
            historicalData=HistoricalData(
                revenueGrowth3Y=rev_growth_values[0],
                revenueGrowth2Y=rev_growth_values[1], 
                revenueGrowth1Y=rev_growth_values[2],
                dilution3Y=dilution_values[0],
                dilution2Y=dilution_values[1],
                dilution1Y=dilution_values[2],
                fcfMargin3Y=fcf_margin_values[0],
                fcfMargin2Y=fcf_margin_values[1],
                fcfMargin1Y=fcf_margin_values[2]
            )
        )
        
        logger.info(f"Successfully fetched company info for {request.ticker}")
        return company_data
        
    except Exception as e:
        logger.error(f"Error fetching company info for {request.ticker}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=f"Failed to fetch company information: {str(e)}")

@app.post("/api/calculate_dcf", response_model=DCFResults)
async def calculate_dcf_endpoint(request: DCFCalculationRequest):
    """
    Calculate DCF using the existing dcf function
    """
    try:
        logger.info(f"Calculating DCF for ticker: {request.ticker}")
        
        # First get company info
        current_price, total_shares, prev_rev_growth, starting_rev, prev_fcf_margin, info_str, extra_info = get_info(request.ticker.upper())
        
        # Call the existing DCF calculation function
        results = dcf(
            rev_growth_array=request.revenueGrowthRate / 100,  # Convert percentage to decimal
            fcf_margins_array=request.fcfMargin / 100,         # Convert percentage to decimal
            n_future_years=request.numberOfYears,
            latest_revenue=starting_rev,
            wacc=request.discountRate / 100,                   # Convert percentage to decimal
            tgr=request.terminalGrowthRate / 100,              # Convert percentage to decimal
            total_shares=total_shares,
            current_price=current_price
        )
        
        # Unpack results: fair_value, req_rg, req_wacc, req_fcf, assumed_cagr
        fair_value, required_revenue_growth, required_wacc, required_fcf_margin, assumed_cagr = results
        
        # Calculate additional metrics
        upside_downside = ((fair_value - current_price) / current_price) * 100
        yearly_revenue_after_n = starting_rev * ((1 + request.revenueGrowthRate/100) ** request.numberOfYears)
        compounded_return_rate = required_wacc  # This is already calculated by the backend
        
        # Determine currency for formatting
        currency = "INR" if ".NS" in request.ticker.upper() else "USD"
        
        # Format the yearly revenue after N years for proper display
        formatted_yearly_revenue = format_number_for_display(yearly_revenue_after_n, currency)
        
        dcf_results = DCFResults(
            fairValue=fair_value,
            currentPrice=current_price,
            upsideDownside=upside_downside,
            yearlyRevenueAfterNYears=formatted_yearly_revenue,
            requiredRevenueGrowth=required_revenue_growth,
            requiredFCFMargin=required_fcf_margin,
            compoundedReturnRate=compounded_return_rate
        )
        
        logger.info(f"Successfully calculated DCF for {request.ticker}")
        return dcf_results
        
    except Exception as e:
        logger.error(f"Error calculating DCF for {request.ticker}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=f"Failed to calculate DCF: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running"}

# Mount static files for React app (if built)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    @app.get("/")
    async def read_react_app():
        """Serve the React app"""
        index_file = os.path.join(static_dir, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        else:
            return FileResponse('index.html')  # Fallback to API documentation
    
    # Catch all route for React Router (SPA routing)
    @app.get("/{path:path}")
    async def catch_all(path: str):
        """Catch-all route to serve React app for client-side routing"""
        # Don't intercept API routes
        if path.startswith("api/") or path.startswith("health"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        
        # Serve React app for all other routes
        index_file = os.path.join(static_dir, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        else:
            raise HTTPException(status_code=404, detail="Page not found")
else:
    @app.get("/")
    async def read_index():
        """Serve the main HTML page (fallback when React app not built)"""
        return FileResponse('index.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("api_server:app", host="0.0.0.0", port=port)