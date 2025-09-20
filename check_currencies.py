#!/usr/bin/env python3
"""
Check the actual financial currency for TCS and INFY directly from yfinance
"""
import yfinance as yf

def check_financial_currency(ticker):
    print(f"\n{ticker}:")
    stock = yf.Ticker(ticker)
    info = stock.info
    print(f"  Currency: {info.get('currency', 'N/A')}")
    print(f"  Financial Currency: {info.get('financialCurrency', 'N/A')}")
    
    # Get revenue from income statement
    income = stock.income_stmt
    if not income.empty and 'Total Revenue' in income.index:
        revenue = income.loc['Total Revenue'].iloc[0]
        print(f"  Total Revenue: {revenue:,}")

if __name__ == "__main__":
    check_financial_currency("TCS.NS")
    check_financial_currency("INFY.NS")
    check_financial_currency("RELIANCE.NS")  # Another Indian stock for comparison