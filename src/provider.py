'''
Authored by: @akashaero
07/26/2023

Provides important utilities to main programs for stock valuation
'''

import numpy as np
import yfinance as yf
import os, csv, time
from tabulate import tabulate
from scipy.optimize import minimize_scalar
import functools

# Add shared session for yfinance to fix 429 errors on EC2
try:
    from curl_cffi import requests as curl_requests
    USE_CURL_CFFI = True
except ImportError:
    import requests as curl_requests
    USE_CURL_CFFI = False

import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

def make_session():
    if USE_CURL_CFFI:
        # Use curl_cffi session for latest yfinance
        s = curl_requests.Session()
        s.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        })
        return s
    else:
        # Fallback to regular requests session
        s = requests.Session()
        s.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        })
        retry = Retry(
            total=5, 
            backoff_factor=0.8, 
            status_forcelist=[429,500,502,503,504], 
            allowed_methods=["GET","HEAD"]
        )
        adapter = HTTPAdapter(max_retries=retry, pool_connections=20, pool_maxsize=20)
        s.mount("https://", adapter)
        s.mount("http://", adapter)
        return s

# Create shared session
shared_session = make_session()

# Fallback function for when yfinance fails completely
def get_basic_stock_data(ticker):
    """Fallback method using direct Yahoo Finance API when yfinance fails"""
    import time
    import random
    
    time.sleep(random.uniform(1, 3))
    
    try:
        # Try direct API call
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://finance.yahoo.com/'
        }
        
        if USE_CURL_CFFI:
            response = curl_requests.get(url, headers=headers, timeout=15)
        else:
            response = requests.get(url, headers=headers, timeout=15)
            
        if response.status_code == 200:
            data = response.json()
            chart = data.get('chart', {}).get('result', [{}])[0]
            meta = chart.get('meta', {})
            
            return {
                'regularMarketPrice': meta.get('regularMarketPrice', 0),
                'currency': meta.get('currency', 'INR'),
                'marketCap': meta.get('marketCap'),
                'sharesOutstanding': meta.get('sharesOutstanding'),
                'financialCurrency': meta.get('currency', 'INR')
            }
    except Exception as e:
        print(f"Fallback method also failed for {ticker}: {e}")
        
    return None

currency_symbols = {'USD':'$', 'JPY':'¥', 'AUD':'$', 'NZD':'$', 'EUR':'€', 'GBP':'£', 'ARS':'$', 'HKD':'$', 'INR':'₹', 'CAD':'$', 'MXN':'$', 'IDR':'Rp.', 'SGD':'$', 'CNY':'CN¥', 'TWD':'$'}
# Hardcoded conversion multiples - all set to 1.0 to eliminate currency conversion
conversion_multiples = {'USD':1.0, 'JPY':1.0, 'AUD':1.0, 'NZD':1.0, 'EUR':1.0, 'GBP':1.0, 'ARS':1.0, 'HKD':1.0, 'INR':1.0, 'CAD':1.0, 'MXN':1.0, 'IDR':1.0, 'SGD':1.0, 'CNY':1.0, 'TWD':1.0}

def get_out_str(num):
  if num is np.isnan(num): return num
  elif num > 1000.0 and num < 1000000.0: return str(np.round(num/1000.0, 2))+'K'
  elif num > 1000000.0 and num < 1000000000.0: return str(np.round(num/1000000.0, 2))+'M'
  elif num > 1000000000.0 and num < 1000000000000.0: return str(np.round(num/1000000000.0, 2))+'B'
  elif num > 1000000000000.0: return str(np.round(num/1000000000000.0, 2))+'T'
  return num

def not_a_float(num):
  if not type(num) == float:
    return True
  else:
    return False

@functools.cache
def get_info(ticker):
  import time
  import random
  
  # Add aggressive delay to avoid rate limiting
  delay = random.uniform(2, 5)
  print(f"Waiting {delay:.1f}s before fetching {ticker}...")
  time.sleep(delay)
  
  max_retries = 3
  for attempt in range(max_retries):
    try:
      if attempt > 0:
        retry_delay = 10 * (2 ** attempt) + random.uniform(0, 5)
        print(f"Retry {attempt} for {ticker} after {retry_delay:.1f}s...")
        time.sleep(retry_delay)
      
      stock      = yf.Ticker(ticker, session=shared_session)
      income     = stock.income_stmt
      cashflow   = stock.cashflow
      stock_info = stock.info
      
      # Check if we got valid data
      if not stock_info or len(stock_info) < 5:
        raise Exception("Empty or invalid stock info received")
      
      break  # Success, exit retry loop
      
    except Exception as e:
      error_str = str(e).lower()
      if "429" in error_str or "too many requests" in error_str:
        if attempt == max_retries - 1:
          # Try fallback method before giving up
          print(f"yfinance failed for {ticker}, trying fallback method...")
          fallback_data = get_basic_stock_data(ticker)
          if fallback_data:
            print(f"✅ Fallback method succeeded for {ticker}")
            # Create minimal data structure for fallback
            stock_info = fallback_data
            income = None  # No income data in fallback
            cashflow = None  # No cashflow data in fallback
            break
          else:
            raise Exception(f"Yahoo Finance rate limit exceeded for {ticker}. Both primary and fallback methods failed.")
        continue
      elif "404" in error_str or "not found" in error_str:
        raise Exception(f"Ticker {ticker} not found. Please check the symbol.")
      else:
        if attempt == max_retries - 1:
          raise Exception(f"Failed to fetch data for {ticker}: {str(e)}")
        continue

  # 3 years, 2 years, 1 year
  def get_rates(df):
    results = []
    for i in range(len(df) - 1):
      if np.isnan(df.iloc[0]) or np.isnan(df.iloc[(len(df) - 1)-i]):
        results.append('-')
      else:
        results.append(((df.iloc[0] / df.iloc[(len(df) - 1)-i])**(1/((len(df)-1)-i))) - 1)
    return results

  # 3 years, 2 years, 1 year
  def get_margins(r, fcf):
    results = []
    n = min(len(r), len(fcf))
    for i in range(n-1):
      if np.isnan(fcf.iloc[i]) or np.isnan(r.iloc[i]):
        results.append('-')
      else:
        results.append(fcf.iloc[i]/r.iloc[i])
    results.reverse()
    return results

  def make_list(label, ar):
    if len(ar) > 3:
      ar = ar[1:]
    tmp_list = [label, '-', '-', '-']
    if len(ar) == 2:
      start_idx = 2
    elif len(ar) == 1:
      start_idx = 3
    else:
      start_idx = 1
    for i in range(len(ar)):
      if ar[0] != '-':
        tmp_list[start_idx] = str(round(100*ar[i], 2))+'%'
      start_idx += 1
      if start_idx >= len(tmp_list):
        break;
    return tmp_list[0:4]

  starting_fcf    = float(cashflow.loc['Free Cash Flow'].iloc[0]) if not np.isnan(cashflow.loc['Free Cash Flow'].iloc[0]) else '-'
  starting_rev    = float(income.loc['Total Revenue'].iloc[0]) if not np.isnan(income.loc['Total Revenue'].iloc[0]) else '-'
  FCF_Margin      = round(100*starting_fcf / starting_rev, 2) if not starting_fcf == '-' or not starting_rev == '-' else '-'
  current_price   = round(stock_info['currentPrice'] / conversion_multiples.get(stock_info.get('currency', 'USD'), 1.0), 2) if 'currentPrice' in stock_info else '-'
  total_shares    = stock_info['sharesOutstanding'] if 'sharesOutstanding' in stock_info else income.loc['Basic Average Shares'].iloc[0]
  starting_rev    = income.loc['Total Revenue'].iloc[0]
  rev_growth      = get_rates(income.loc['Total Revenue'])
  buybacks        = get_rates(income.loc['Diluted Average Shares'])
  fcf_growth      = get_rates(cashflow.loc['Free Cash Flow'])
  fcf_margins     = get_margins(income.loc['Total Revenue'], cashflow.loc['Free Cash Flow'])
  prev_rev_growth = rev_growth[-1]
  prev_fcf_margin = fcf_margins[-1]

  business_name   = stock_info['shortName'] if 'shortName' in stock_info else stock_info.get('longName', ticker)
  fwdPE           = np.round(stock_info['forwardPE'], 2) if 'forwardPE' in stock_info and not np.isnan(stock_info['forwardPE']) else '-'
  currency        = stock_info['currency'] if 'currency' in stock_info else 'USD'
  financial_curr  = stock_info['financialCurrency'] if 'financialCurrency' in stock_info else currency
  PEG             = stock_info['trailingPegRatio'] if 'trailingPegRatio' in stock_info and type(stock_info['trailingPegRatio']) == float else '-'
  
  # if not np.isnan(stock_info['trailingPegRatio'] if 'trailingPegRatio' in stock_info else np.nan) else '-'

  # float % of total shares outstanding
  floatShares      = stock_info['floatShares'] if 'floatShares' in stock_info and not np.isnan(stock_info['floatShares']) else '-'
  if total_shares != '-' and floatShares != '-':
    percFloat = str(np.round(100.*(floatShares / total_shares), 2))+'%'
  else:
    percFloat = '-'
  
  percent_short = str(np.round(stock_info['shortPercentOfFloat']*100., 2))+'%' if 'shortPercentOfFloat' in stock_info and not np.isnan(stock_info['shortPercentOfFloat']) else '-'

  # Covert all these to Thousands, Millions or Billions if not in tens
  avgVol           = get_out_str(float(stock_info['averageVolume'])) if 'averageVolume' in stock_info and not np.isnan(stock_info['averageVolume']) else '-'
  mcap             = '$'+get_out_str(float(stock_info['marketCap'] / conversion_multiples.get(currency, 1.0))) if 'marketCap' in stock_info and not np.isnan(stock_info['marketCap']) else '-'

  # For populating stock related data - include financial currency for USD conversion detection
  extra_info = ['$'+get_out_str(starting_rev / conversion_multiples.get(financial_curr, 1.0)), get_out_str(total_shares), percFloat, percent_short, avgVol, mcap, conversion_multiples.get(financial_curr, 1.0), financial_curr]
  
  # # [Maybe in future]
  # business_summary = stock_info['longBusinessSummary'] if not np.isnan(stock_info['longBusinessSummary']) else '-'
  # book_val         = stock_info['bookValue'] if not np.isnan(stock_info['bookValue']) else '-'
  # pb               = stock_info['priceToBook'] if not np.isnan(stock_info['priceToBook']) else '-'
  # ttm_PS           = stock_info['priceToSalesTrailing12Months'] if not np.isnan(stock_info['priceToSalesTrailing12Months']) else '-'
  # total_debt       = stock_info['totalDebt'] if not np.isnan(stock_info['totalDebt']) else '-'
  # ROA              = stock_info['returnOnAssets'] if not np.isnan(stock_info['returnOnAssets']) else '-'
  # ROE              = stock_info['returnOnEquity'] if not np.isnan(stock_info['returnOnEquity']) else '-'

  if 'forwardPE' in stock_info and 'trailingPegRatio' in stock_info:
    if not_a_float(fwdPE) or not_a_float(PEG):
      analyst_growth = '-'
    elif PEG == 0.0:
      analyst_growth = '-'
    else:
      analyst_growth  = str(round(fwdPE / PEG, 2))+'%'
  else:
    analyst_growth = '-'

  header = [business_name+' ({})'.format(currency), '3 Years', '2 Years', '1 Year']
  table_data = []
  table_data.append(make_list('Revenue Growth', rev_growth))
  table_data.append(make_list('Dilution(+)/Buybacks(-)', buybacks))
  table_data.append(make_list('FCF Margins', fcf_margins))
  table_data.append(['Analyst Expected Growth (5Y)', analyst_growth, '-', '-'])
  return current_price, total_shares, prev_rev_growth, starting_rev / conversion_multiples.get(financial_curr, 1.0), prev_fcf_margin, tabulate(table_data, headers=header), extra_info

def dcf(rev_growth_array, fcf_margins_array, n_future_years, latest_revenue, \
        wacc, tgr, total_shares, current_price, reverse_dcf_mode=False):
  if np.array([rev_growth_array]).shape == (1,):
    rev_growth_array = np.full(n_future_years, rev_growth_array)

  if np.array([fcf_margins_array]).shape == (1,):
    fcf_margins_array = np.full(n_future_years, fcf_margins_array)

  # Project FCF
  proj_fcf = []
  rev_inc = latest_revenue
  for i in range(0, n_future_years):
    rev_inc = rev_inc * (1+rev_growth_array[i])
    proj_fcf.append(rev_inc*fcf_margins_array[i])

  # Get discount factors
  discount_factors = []
  for i in range(0,n_future_years):
    discount_factors.append((1+wacc)**(i+1))

  # Total discounted fcf for n_future_years
  discounted_fcf = 0
  for i, p in enumerate(proj_fcf):
    discounted_fcf += p/discount_factors[i]

  # Terminal value (discounted)
  terminal_value = (proj_fcf[-1] * (1+tgr))/(wacc - tgr)
  terminal_value /= discount_factors[-1]

  # Total value for all shares
  todays_value = discounted_fcf + terminal_value

  # Fair value per share.
  fair_value = todays_value/total_shares

  assumed_cagr = calc_cagr(rev_growth_array, n_future_years)

  if reverse_dcf_mode:
    return fair_value

  # Reverse DCF Functions
  def reverse_dcf_revenue(rev_growth_rate, fcf_margins_array, n_future_years, \
                        latest_revenue, wacc, tgr, total_shares, current_price):
    return abs(dcf(np.full(n_future_years,rev_growth_rate), fcf_margins_array, \
                           n_future_years, latest_revenue, wacc, tgr, total_shares, current_price, reverse_dcf_mode=True)\
               - current_price)

  def reverse_dcf_fcf_margin(fcf_margin, rev_growth_array, n_future_years, \
                             latest_revenue, wacc, tgr, total_shares, \
                             current_price):
    return abs(dcf(rev_growth_array, np.full(n_future_years,fcf_margin), \
                   n_future_years, latest_revenue, wacc, tgr, total_shares, current_price, reverse_dcf_mode=True) \
               - current_price)

  def reverse_dcf_discount_rate(wacc, rev_growth_array, fcf_margins_array, \
                                n_future_years, latest_revenue, tgr, \
                                total_shares, current_price):
    return abs(dcf(rev_growth_array, fcf_margins_array, n_future_years, \
                   latest_revenue, wacc, tgr, total_shares, current_price, reverse_dcf_mode=True) - current_price)

  required_rev_growth    = round(100*minimize_scalar(reverse_dcf_revenue, \
                         args=(fcf_margins_array, n_future_years, latest_revenue, \
                               wacc, tgr, total_shares, \
                               current_price)).x, 2)

  required_discount_rate = round(100*minimize_scalar(reverse_dcf_discount_rate, \
                           args=(rev_growth_array, fcf_margins_array, n_future_years, \
                                 latest_revenue, tgr, total_shares, \
                                 current_price)).x, 2)

  required_fcf_margin    = round(100*minimize_scalar(reverse_dcf_fcf_margin, \
                           args=(rev_growth_array, n_future_years, latest_revenue, \
                                 wacc, tgr, total_shares, \
                                 current_price)).x, 2)

  

  return round(fair_value, 2), required_rev_growth, required_discount_rate, required_fcf_margin, assumed_cagr

def calc_up_downside(fair_value, current_price):
  if fair_value > current_price:
    # Stock is undervalued compared to current price
    return round(((fair_value-current_price)/current_price)*100, 2)
  else:
    # Current price is overvalued compared to fair value
    return round(-100*((current_price - fair_value)/current_price), 2)

def print_calculated_info(results, current_price, fcf_margins, prev_rev_growth, \
                          prev_fcf_margin, tkr, tgr, wacc, n_future_years):
  fv, r_rg, r_wacc, r_fcf, rev_growth = results
  if np.array([fcf_margins]).shape == (1,):
    pass
  else:
    fcf_margins = np.average(np.array(fcf_margins))

  print('Based on your inputs, for next {} years,'.format(n_future_years))
  print('Assuming {}% of average annual revenue growth,'.format(rev_growth))
  print('         {}% of free cash flow margin, and'.format(fcf_margins))
  print('         {}% of terminal growth rate,\n'.format(tgr))
  print('The fair value for {} stock is ${} to get {}% of annualized return for next {} years.'\
        .format(tkr, fv, wacc, n_future_years))
  print('\nBased on previous close price of ${}, the upside/downside is {}%'\
       .format(current_price, calc_up_downside(fv, current_price)))
  print('\nTo justify the current stock price of ${}, Either,'\
        .format(current_price))
  print('{} would have to grow at {}% average annual rate for next {} years'\
        .format(tkr, r_rg, n_future_years))
  print('  or     have free cash flow margin of {}%'\
        .format(r_fcf))
  print('  or     you get {}% annualized return for next {} years compared to assumed {}% '\
        .format(r_wacc, n_future_years, wacc))

def get_calculated_info(results, current_price, fcf_margins, prev_rev_growth, \
                          prev_fcf_margin, tkr, tgr, wacc, n_future_years):
  fv, r_rg, r_wacc, r_fcf, rev_growth = results
  if np.array([fcf_margins]).shape == (1,):
    pass
  else:
    fcf_margins = np.average(np.array(fcf_margins))

  out_str = ''
  out_str += ('Based on your inputs, for next {} years,'.format(n_future_years))
  out_str += ('Assuming {}% of average annual revenue growth,'.format(rev_growth))
  out_str += ('         {}% of free cash flow margin, and'.format(fcf_margins))
  out_str += ('         {}% of terminal growth rate,\n'.format(tgr))
  out_str += ('The fair value for {} stock is ${} to get {}% of annualized return for next {} years.'\
        .format(tkr, fv, wacc, n_future_years))
  out_str += ('\nBased on previous close price of ${}, the upside/downside is {}%'\
       .format(current_price, calc_up_downside(fv, current_price)))
  out_str += ('\nTo justify the current stock price of ${}, Either,'\
        .format(current_price))
  out_str += ('{} would have to grow at {}% average annual rate for next {} years'\
        .format(tkr, r_rg, n_future_years))
  out_str += ('  or     have free cash flow margin of {}%'\
        .format(r_fcf))
  out_str += ('  or     you get {}% annualized return for next {} years compared to assumed {}% '\
        .format(r_wacc, n_future_years, wacc))
  return out_str

def calc_cagr(rev_growth_array, N):
  if np.array([rev_growth_array]).shape == (1,):
    return round(100*rev_growth_array, 2)
  final_val = 1
  for r in rev_growth_array:
    final_val *= (1+r)
  return round(np.sign(final_val)*100*(np.abs(final_val/1)**(1/N) - 1), 2)

def write_batch_mode_csv(fname, data):
  if not os.path.exists('./batch_mode_files/results'):
    os.mkdir('./batch_mode_files/results')
  csv_header = ['stock', 'fair_value', 'current_price', 'upside/(downside)', \
                'assumed_revenue_growth(%)', 'assumed_fcf_margin (%)', \
                'current_price_rev_growth (%)', 'current_price_fcf_margin (%)', \
                'current_price_required_return (%)']
  timestr = time.strftime("%Y%m%d-%H%M%S")
  print('Writing All Results in {} .....'.format('./batch_mode_files/results/'+timestr+'_'+fname))
  with open('./batch_mode_files/results/'+timestr+'_'+fname, 'w', newline='') as f:
    write = csv.writer(f)
    write.writerow(csv_header)
    write.writerows(data)