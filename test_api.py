#!/usr/bin/env python3
"""Test script to validate the API data parsing"""

import sys
import asyncio
sys.path.append('.')

from api_server import get_company_info, CompanyInfoRequest

async def test_api_parsing():
    """Test the API data parsing directly"""
    print("Testing API data parsing...")
    
    # Create test request
    request = CompanyInfoRequest(ticker="INFY.NS")
    
    try:
        # Call the API function directly
        result = await get_company_info(request)
        
        print(f"Company Name: {result.name}")
        print(f"Current Price: {result.currentPrice}")
        print(f"Currency: {result.currency}")
        print(f"Last Yearly Revenue: {result.lastYearlyRevenue}")
        print(f"Total Shares Out: {result.totalSharesOut}")
        
        print("\nHistorical Data:")
        print(f"  Revenue Growth 3Y: {result.historicalData.revenueGrowth3Y}%")
        print(f"  Revenue Growth 2Y: {result.historicalData.revenueGrowth2Y}%")
        print(f"  Revenue Growth 1Y: {result.historicalData.revenueGrowth1Y}%")
        print(f"  Dilution 3Y: {result.historicalData.dilution3Y}%")
        print(f"  Dilution 2Y: {result.historicalData.dilution2Y}%")
        print(f"  Dilution 1Y: {result.historicalData.dilution1Y}%")
        print(f"  FCF Margin 3Y: {result.historicalData.fcfMargin3Y}%")
        print(f"  FCF Margin 2Y: {result.historicalData.fcfMargin2Y}%")
        print(f"  FCF Margin 1Y: {result.historicalData.fcfMargin1Y}%")
        
        print(f"\nMarket Cap: {result.marketCap}")
        print(f"Float Percent: {result.totalFloatPercent}")
        
        print("\n✅ API parsing test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ API parsing test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_api_parsing())