#!/usr/bin/env python3
"""Debug DCF calculation step by step"""

import numpy as np

def debug_dcf_calculation():
    # Infosys parameters (in crores)
    starting_revenue = 192770  # crores
    rev_growth_rate = 0.12
    fcf_margin = 0.25
    n_years = 7
    discount_rate = 0.10
    terminal_growth = 0.025
    total_shares = 41452.9  # crores
    
    print("=== Manual DCF Calculation for Infosys ===")
    print(f"Starting Revenue: ₹{starting_revenue:,} Cr")
    print(f"Growth Rate: {rev_growth_rate*100}%")
    print(f"FCF Margin: {fcf_margin*100}%")
    print(f"Years: {n_years}")
    print(f"Discount Rate: {discount_rate*100}%")
    print(f"Terminal Growth: {terminal_growth*100}%")
    print(f"Total Shares: {total_shares:,} Cr")
    print()
    
    # Step 1: Project revenues and FCFs
    print("Year-by-Year Projections:")
    projected_fcfs = []
    revenue = starting_revenue
    
    for year in range(1, n_years + 1):
        revenue = revenue * (1 + rev_growth_rate)
        fcf = revenue * fcf_margin
        projected_fcfs.append(fcf)
        
        discount_factor = (1 + discount_rate) ** year
        present_value = fcf / discount_factor
        
        print(f"Year {year}:")
        print(f"  Revenue: ₹{revenue:,.0f} Cr")
        print(f"  FCF: ₹{fcf:,.0f} Cr")
        print(f"  Discount Factor: {discount_factor:.4f}")
        print(f"  Present Value: ₹{present_value:,.0f} Cr")
        print()
    
    # Step 2: Calculate present value of FCFs
    total_pv_fcf = 0
    for i, fcf in enumerate(projected_fcfs):
        discount_factor = (1 + discount_rate) ** (i + 1)
        pv = fcf / discount_factor
        total_pv_fcf += pv
    
    print(f"Total Present Value of FCFs: ₹{total_pv_fcf:,.0f} Cr")
    
    # Step 3: Calculate terminal value
    terminal_fcf = projected_fcfs[-1] * (1 + terminal_growth)
    terminal_value = terminal_fcf / (discount_rate - terminal_growth)
    terminal_discount_factor = (1 + discount_rate) ** n_years
    pv_terminal_value = terminal_value / terminal_discount_factor
    
    print(f"\nTerminal Value Calculation:")
    print(f"Terminal FCF (Year {n_years+1}): ₹{terminal_fcf:,.0f} Cr")
    print(f"Terminal Value: ₹{terminal_value:,.0f} Cr")
    print(f"Terminal Discount Factor: {terminal_discount_factor:.4f}")
    print(f"PV of Terminal Value: ₹{pv_terminal_value:,.0f} Cr")
    
    # Step 4: Total enterprise value
    enterprise_value = total_pv_fcf + pv_terminal_value
    print(f"\nTotal Enterprise Value: ₹{enterprise_value:,.0f} Cr")
    
    # Step 5: Fair value per share
    fair_value_per_share = enterprise_value / total_shares
    print(f"Fair Value per Share: ₹{fair_value_per_share:.2f}")
    
    # Check if this seems reasonable
    print(f"\nSanity Check:")
    print(f"Current Infosys Price: ~₹1,540")
    print(f"Our Calculated Fair Value: ₹{fair_value_per_share:.2f}")
    print(f"Difference: {((fair_value_per_share - 1540) / 1540) * 100:.1f}%")
    
if __name__ == "__main__":
    debug_dcf_calculation()