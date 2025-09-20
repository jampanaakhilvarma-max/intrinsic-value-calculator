#!/usr/bin/env python3
"""Quick test for Infosys DCF calculation"""

from src.provider import get_info, dcf, calc_up_downside

def test_infy_valuation():
    ticker = "INFY.NS"
    
    print(f"Testing DCF calculation for {ticker}")
    print("="*50)
    
    # Get company data
    try:
        current_price, total_shares, prev_rev_growth, starting_rev, prev_fcf_margin, info_data, extra_info = get_info(ticker)
        
        print("Company Data:")
        print(f"Current Price: ₹{current_price}")
        print(f"Total Shares: {total_shares:,}")
        print(f"Starting Revenue: ₹{starting_rev:,}")
        print(f"Previous FCF Margin: {prev_fcf_margin*100:.2f}%")
        print()
        
        print("Historical Data:")
        print(info_data)
        print()
        
        # Test DCF with reasonable assumptions
        rev_growth_rate = 0.12  # 12%
        fcf_margin = 0.25       # 25%
        n_years = 7
        discount_rate = 0.10    # 10%
        terminal_growth = 0.025 # 2.5%
        
        print("DCF Assumptions:")
        print(f"Revenue Growth: {rev_growth_rate*100}%")
        print(f"FCF Margin: {fcf_margin*100}%")
        print(f"Years: {n_years}")
        print(f"Discount Rate: {discount_rate*100}%")
        print(f"Terminal Growth: {terminal_growth*100}%")
        print()
        
        # Calculate DCF
        results = dcf(rev_growth_rate, fcf_margin, n_years, starting_rev, discount_rate, terminal_growth, total_shares, current_price)
        fair_value, required_rev_growth, required_discount_rate, required_fcf_margin, assumed_cagr = results
        
        print("DCF Results:")
        print(f"Fair Value: ₹{fair_value}")
        print(f"Current Price: ₹{current_price}")
        print(f"Upside/Downside: {calc_up_downside(fair_value, current_price):.2f}%")
        print()
        
        # Debug calculations step by step
        print("Step-by-Step DCF Debug:")
        print(f"1. Starting Revenue: ₹{starting_rev:,}")
        print(f"2. Revenue Growth Rate: {rev_growth_rate*100}%")
        print(f"3. FCF Margin: {fcf_margin*100}%")
        
        # Calculate projected revenues manually
        projected_revenues = []
        rev_temp = starting_rev
        for year in range(1, n_years + 1):
            rev_temp = rev_temp * (1 + rev_growth_rate)
            projected_revenues.append(rev_temp)
            print(f"   Year {year} Revenue: ₹{rev_temp:,.0f}")
        
        # Calculate FCFs
        projected_fcfs = []
        for i, revenue in enumerate(projected_revenues):
            fcf = revenue * fcf_margin
            projected_fcfs.append(fcf)
            print(f"   Year {i+1} FCF: ₹{fcf:,.0f}")
        
        print(f"4. Total Shares: {total_shares:,}")
        print(f"5. Discount Rate: {discount_rate*100}%")
        
        # Check if starting_rev needs to be in different units
        print(f"\nUnit Check:")
        print(f"Starting Revenue: ₹{starting_rev:,}")
        print(f"If in lakhs: ₹{starting_rev*100000:,}")  
        print(f"If in crores: ₹{starting_rev*10000000:,}")
        
        print("Debug Information:")
        print(f"Starting Revenue (raw): {starting_rev:,}")
        print(f"Starting Revenue (Cr): {starting_rev/10000000:.2f} Cr")
        print(f"Total Shares (raw): {total_shares:,}")
        print(f"Total Shares (Cr): {total_shares/10000000:.2f} Cr")
        
        # Test with historical FCF margin
        if prev_fcf_margin and prev_fcf_margin > 0:
            print(f"\nTesting with historical FCF margin: {prev_fcf_margin*100:.2f}%")
            results_hist = dcf(rev_growth_rate, prev_fcf_margin, n_years, starting_rev, discount_rate, terminal_growth, total_shares, current_price)
            fair_value_hist = results_hist[0]
            print(f"Fair Value with historical FCF margin: ₹{fair_value_hist}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_infy_valuation()