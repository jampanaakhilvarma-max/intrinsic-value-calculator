#!/usr/bin/env python3
"""
Test script to verify DCF calculations are working correctly with currency conversion
"""
import sys
sys.path.append('src')

from provider import get_info, dcf

def test_dcf_calculation(ticker, expected_currency):
    print(f"\n{'='*60}")
    print(f"TESTING DCF CALCULATION FOR {ticker}")
    print(f"{'='*60}")
    
    try:
        # Get company data
        current_price, total_shares, prev_rev_growth, starting_rev, prev_fcf_margin, info_data, extra_info = get_info(ticker)
        
        print(f"Raw Data from Provider:")
        print(f"  Current Price: {current_price}")
        print(f"  Starting Revenue: {starting_rev:,}")
        print(f"  Total Shares: {total_shares:,}")
        print(f"  Extra Info Length: {len(extra_info)}")
        for i, item in enumerate(extra_info):
            print(f"  Extra Info[{i}]: {repr(item)}")
        
        # Get currency from info_data
        currency_match = info_data.split('(')[1].split(')')[0] if '(' in info_data and ')' in info_data else 'USD'
        
        # Check if we need USD to INR conversion
        financials_in_usd = False
        if isinstance(extra_info, list) and len(extra_info) > 7:
            financial_currency = extra_info[7]  # This is the actual financial currency from yfinance
            print(f"  Financial Currency: {financial_currency}")
            # If stock currency is INR but financials are in USD
            if currency_match == "INR" and financial_currency == "USD":
                financials_in_usd = True
        else:
            print(f"  Financial Currency: Not available (extra_info too short)")
        
        print(f"  Currency Match: {currency_match}")
        print(f"  Financials in USD: {financials_in_usd}")
        
        # Apply currency conversion if needed
        if financials_in_usd and currency_match == "INR":
            usd_to_inr_rate = 83.0
            starting_rev_dcf = starting_rev * usd_to_inr_rate
            print(f"  USD to INR Conversion Applied: {starting_rev:,} * {usd_to_inr_rate} = {starting_rev_dcf:,}")
        else:
            starting_rev_dcf = starting_rev
            print(f"  No conversion needed: {starting_rev_dcf:,}")
        
        # Test DCF calculation with standard parameters
        rev_growth_rate = 0.15  # 15%
        fcf_margin = 0.20       # 20%
        n_years = 7
        discount_rate = 0.10    # 10%
        terminal_growth = 0.06  # 6%
        
        print(f"\nDCF Parameters:")
        print(f"  Revenue Growth Rate: {rev_growth_rate*100}%")
        print(f"  FCF Margin: {fcf_margin*100}%")
        print(f"  Number of Years: {n_years}")
        print(f"  Discount Rate: {discount_rate*100}%")
        print(f"  Terminal Growth: {terminal_growth*100}%")
        
        # Calculate DCF
        results = dcf(
            rev_growth_rate,
            fcf_margin,
            n_years,
            starting_rev_dcf,
            discount_rate,
            terminal_growth,
            total_shares,
            current_price
        )
        
        fair_value, required_rev_growth, required_discount_rate, required_fcf_margin, assumed_cagr = results
        
        print(f"\nDCF Results:")
        print(f"  Fair Value: ₹{fair_value:.2f}")
        print(f"  Current Price: ₹{current_price:.2f}")
        print(f"  Upside/Downside: {((fair_value/current_price - 1) * 100):.1f}%")
        
        # Calculate projected revenue after N years
        yearly_revenue_after_n_years = (starting_rev_dcf * ((1 + rev_growth_rate) ** n_years)) / 10000000
        print(f"  Projected Revenue (Year {n_years}): ₹{yearly_revenue_after_n_years:,.0f} Cr")
        
        # Sanity checks
        print(f"\nSanity Checks:")
        if fair_value > 0:
            print(f"  ✅ Fair value is positive: ₹{fair_value:.2f}")
        else:
            print(f"  ❌ Fair value is negative or zero: ₹{fair_value:.2f}")
            
        if fair_value > current_price * 0.1 and fair_value < current_price * 10:
            print(f"  ✅ Fair value is reasonable (within 10x of current price)")
        else:
            print(f"  ⚠️ Fair value might be unrealistic (>10x or <0.1x current price)")
            
        if starting_rev_dcf > 1000000000:  # > 1 billion
            print(f"  ✅ Revenue base is substantial: ₹{starting_rev_dcf/10000000:,.0f} Cr")
        else:
            print(f"  ⚠️ Revenue base seems low: ₹{starting_rev_dcf/10000000:,.0f} Cr")
        
    except Exception as e:
        print(f"❌ Error in DCF calculation: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Test both companies
    test_dcf_calculation("TCS.NS", "INR")
    test_dcf_calculation("INFY.NS", "INR")