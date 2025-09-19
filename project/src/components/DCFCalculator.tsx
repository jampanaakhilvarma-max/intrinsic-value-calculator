import React, { useState } from 'react';
import { Calculator, Search, TrendingUp, DollarSign, BarChart3, Moon, Sun, ArrowRight, Loader2, HelpCircle, Info, ChevronDown } from 'lucide-react';
import { API_ENDPOINTS } from '../config/api';

interface CompanyData {
  ticker: string;
  name: string;
  lastYearlyRevenue: number;
  totalSharesOut: number;
  totalFloatPercent?: number;
  totalShortPercent?: number;
  averageVolume?: number;
  marketCap?: number;
  currentPrice: number;
  currency: string;
  historicalData: {
    revenueGrowth3Y: number;
    revenueGrowth2Y: number;
    revenueGrowth1Y: number;
    dilution3Y: number;
    dilution2Y: number;
    dilution1Y: number;
    fcfMargin3Y: number;
    fcfMargin2Y: number;
    fcfMargin1Y: number;
  };
}

interface DCFInputs {
  revenueGrowthRate: number;
  fcfMargin: number;
  numberOfYears: number;
  discountRate: number;
  terminalGrowthRate: number;
}

interface DCFResults {
  fairValue: number;
  currentPrice: number;
  upsideDownside: number;
  yearlyRevenueAfterNYears: number;
  requiredRevenueGrowth: number;
  requiredFCFMargin: number;
  compoundedReturnRate: number;
}

// Comprehensive Indian stocks database
const POPULAR_INDIAN_STOCKS = [
  // Large Cap - Most Popular
  { symbol: 'RELIANCE.NS', name: 'Reliance Industries Ltd', sector: 'Oil & Gas', mcap: 'Large' },
  { symbol: 'TCS.NS', name: 'Tata Consultancy Services', sector: 'IT Services', mcap: 'Large' },
  { symbol: 'HDFCBANK.NS', name: 'HDFC Bank Ltd', sector: 'Banking', mcap: 'Large' },
  { symbol: 'INFY.NS', name: 'Infosys Ltd', sector: 'IT Services', mcap: 'Large' },
  { symbol: 'ICICIBANK.NS', name: 'ICICI Bank Ltd', sector: 'Banking', mcap: 'Large' },
  { symbol: 'HINDUNILVR.NS', name: 'Hindustan Unilever Ltd', sector: 'FMCG', mcap: 'Large' },
  { symbol: 'ITC.NS', name: 'ITC Ltd', sector: 'FMCG', mcap: 'Large' },
  { symbol: 'SBIN.NS', name: 'State Bank of India', sector: 'Banking', mcap: 'Large' },
  { symbol: 'BHARTIARTL.NS', name: 'Bharti Airtel Ltd', sector: 'Telecom', mcap: 'Large' },
  { symbol: 'KOTAKBANK.NS', name: 'Kotak Mahindra Bank', sector: 'Banking', mcap: 'Large' },
  { symbol: 'LT.NS', name: 'Larsen & Toubro Ltd', sector: 'Infrastructure', mcap: 'Large' },
  { symbol: 'ASIANPAINT.NS', name: 'Asian Paints Ltd', sector: 'Paints', mcap: 'Large' },
  { symbol: 'MARUTI.NS', name: 'Maruti Suzuki India Ltd', sector: 'Auto', mcap: 'Large' },
  { symbol: 'TITAN.NS', name: 'Titan Company Ltd', sector: 'Jewelry', mcap: 'Large' },
  { symbol: 'WIPRO.NS', name: 'Wipro Ltd', sector: 'IT Services', mcap: 'Large' },
  
  // Additional Popular Stocks
  { symbol: 'ADANIPORTS.NS', name: 'Adani Ports & SEZ Ltd', sector: 'Ports', mcap: 'Large' },
  { symbol: 'AXISBANK.NS', name: 'Axis Bank Ltd', sector: 'Banking', mcap: 'Large' },
  { symbol: 'BAJFINANCE.NS', name: 'Bajaj Finance Ltd', sector: 'NBFC', mcap: 'Large' },
  { symbol: 'BAJAJFINSV.NS', name: 'Bajaj Finserv Ltd', sector: 'Financial Services', mcap: 'Large' },
  { symbol: 'HCLTECH.NS', name: 'HCL Technologies Ltd', sector: 'IT Services', mcap: 'Large' },
  { symbol: 'HEROMOTOCO.NS', name: 'Hero MotoCorp Ltd', sector: 'Auto', mcap: 'Large' },
  { symbol: 'JSWSTEEL.NS', name: 'JSW Steel Ltd', sector: 'Steel', mcap: 'Large' },
  { symbol: 'M&M.NS', name: 'Mahindra & Mahindra Ltd', sector: 'Auto', mcap: 'Large' },
  { symbol: 'NESTLEIND.NS', name: 'Nestle India Ltd', sector: 'FMCG', mcap: 'Large' },
  { symbol: 'NTPC.NS', name: 'NTPC Ltd', sector: 'Power', mcap: 'Large' },
  { symbol: 'ONGC.NS', name: 'Oil & Natural Gas Corp', sector: 'Oil & Gas', mcap: 'Large' },
  { symbol: 'POWERGRID.NS', name: 'Power Grid Corp of India', sector: 'Power', mcap: 'Large' },
  { symbol: 'SUNPHARMA.NS', name: 'Sun Pharmaceutical Ind', sector: 'Pharma', mcap: 'Large' },
  { symbol: 'TATAMOTORS.NS', name: 'Tata Motors Ltd', sector: 'Auto', mcap: 'Large' },
  { symbol: 'TATASTEEL.NS', name: 'Tata Steel Ltd', sector: 'Steel', mcap: 'Large' },
  { symbol: 'TECHM.NS', name: 'Tech Mahindra Ltd', sector: 'IT Services', mcap: 'Large' },
  { symbol: 'ULTRACEMCO.NS', name: 'UltraTech Cement Ltd', sector: 'Cement', mcap: 'Large' },
  { symbol: 'DRREDDY.NS', name: 'Dr Reddys Laboratories', sector: 'Pharma', mcap: 'Large' },
  { symbol: 'EICHERMOT.NS', name: 'Eicher Motors Ltd', sector: 'Auto', mcap: 'Large' },
  { symbol: 'GRASIM.NS', name: 'Grasim Industries Ltd', sector: 'Cement', mcap: 'Large' },
  { symbol: 'HINDALCO.NS', name: 'Hindalco Industries Ltd', sector: 'Metals', mcap: 'Large' },
  { symbol: 'INDUSINDBK.NS', name: 'IndusInd Bank Ltd', sector: 'Banking', mcap: 'Large' },
  { symbol: 'CIPLA.NS', name: 'Cipla Ltd', sector: 'Pharma', mcap: 'Large' },
  { symbol: 'COALINDIA.NS', name: 'Coal India Ltd', sector: 'Mining', mcap: 'Large' },
  { symbol: 'DIVISLAB.NS', name: 'Divis Laboratories Ltd', sector: 'Pharma', mcap: 'Large' },
  { symbol: 'BRITANNIA.NS', name: 'Britannia Industries Ltd', sector: 'FMCG', mcap: 'Large' },
  { symbol: 'APOLLOHOSP.NS', name: 'Apollo Hospitals Enterprise', sector: 'Healthcare', mcap: 'Large' },
];

// Common stock name mappings for Indian stocks
const INDIAN_STOCK_ALIASES: { [key: string]: string } = {
  'reliance': 'RELIANCE.NS',
  'tcs': 'TCS.NS',
  'tata consultancy': 'TCS.NS',
  'hdfc bank': 'HDFCBANK.NS',
  'hdfc': 'HDFCBANK.NS',
  'infosys': 'INFY.NS',
  'infy': 'INFY.NS',
  'icici': 'ICICIBANK.NS',
  'icici bank': 'ICICIBANK.NS',
  'hindustan unilever': 'HINDUNILVR.NS',
  'hul': 'HINDUNILVR.NS',
  'itc': 'ITC.NS',
  'sbi': 'SBIN.NS',
  'state bank': 'SBIN.NS',
  'bharti': 'BHARTIARTL.NS',
  'airtel': 'BHARTIARTL.NS',
  'kotak': 'KOTAKBANK.NS',
  'lt': 'LT.NS',
  'larsen': 'LT.NS',
  'asian paints': 'ASIANPAINT.NS',
  'maruti': 'MARUTI.NS',
  'titan': 'TITAN.NS',
  'wipro': 'WIPRO.NS',
  'adani ports': 'ADANIPORTS.NS',
  'axis bank': 'AXISBANK.NS',
  'axis': 'AXISBANK.NS',
  'bajaj finance': 'BAJFINANCE.NS',
  'bajaj finserv': 'BAJAJFINSV.NS',
  'hcl': 'HCLTECH.NS',
  'hero': 'HEROMOTOCO.NS',
  'jsw steel': 'JSWSTEEL.NS',
  'mahindra': 'M&M.NS',
  'nestle': 'NESTLEIND.NS',
  'ntpc': 'NTPC.NS',
  'ongc': 'ONGC.NS',
  'power grid': 'POWERGRID.NS',
  'sun pharma': 'SUNPHARMA.NS',
  'tata motors': 'TATAMOTORS.NS',
  'tata steel': 'TATASTEEL.NS',
  'tech mahindra': 'TECHM.NS',
  'ultratech': 'ULTRACEMCO.NS'
};

const DCFCalculator: React.FC = () => {
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [activeTab, setActiveTab] = useState('single');
  const [currentStep, setCurrentStep] = useState(1);
  const [ticker, setTicker] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [companyData, setCompanyData] = useState<CompanyData | null>(null);
  const [dcfInputs, setDCFInputs] = useState<DCFInputs>({
    revenueGrowthRate: 0,
    fcfMargin: 0,
    numberOfYears: 7,
    discountRate: 10,
    terminalGrowthRate: 6
  });
  const [results, setResults] = useState<DCFResults | null>(null);
  const [showTooltip, setShowTooltip] = useState<string | null>(null);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [filteredSuggestions, setFilteredSuggestions] = useState<typeof POPULAR_INDIAN_STOCKS>([]);

  // Smart Indian stock ticker formatting
  const formatIndianTicker = (input: string) => {
    const cleanInput = input.toLowerCase().trim();
    
    // Check if it's a known alias
    if (INDIAN_STOCK_ALIASES[cleanInput]) {
      return INDIAN_STOCK_ALIASES[cleanInput];
    }
    
    // Convert to uppercase and add .NS if not present
    const upperInput = input.toUpperCase().trim();
    
    // If it already has .NS, return as is
    if (upperInput.includes('.NS')) {
      return upperInput;
    }
    
    // If it's a valid looking ticker (2+ chars), add .NS
    if (upperInput.length >= 2 && /^[A-Z&]+$/.test(upperInput.replace('&', ''))) {
      return upperInput + '.NS';
    }
    
    return upperInput;
  };

  // Enhanced filtering for Indian stocks
  const filterIndianSuggestions = (input: string) => {
    if (!input || input.length < 1) {
      // Show top 12 popular stocks when no input
      return POPULAR_INDIAN_STOCKS.slice(0, 12);
    }
    
    const searchTerm = input.toLowerCase();
    
    // Search by multiple criteria
    return POPULAR_INDIAN_STOCKS.filter(stock => {
      const symbol = stock.symbol.toLowerCase();
      const name = stock.name.toLowerCase();
      const sector = stock.sector.toLowerCase();
      const symbolWithoutNS = symbol.replace('.ns', '');
      
      return (
        symbolWithoutNS.includes(searchTerm) ||
        name.includes(searchTerm) ||
        sector.includes(searchTerm) ||
        // Check company name words
        name.split(' ').some(word => word.startsWith(searchTerm))
      );
    }).slice(0, 10);
  };

  // Handle ticker input change
  const handleTickerChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setTicker(value);
    
    const suggestions = filterIndianSuggestions(value);
    setFilteredSuggestions(suggestions);
    setShowSuggestions(true);
  };

  // Handle suggestion selection
  const handleSuggestionSelect = (suggestion: typeof POPULAR_INDIAN_STOCKS[0]) => {
    setTicker(suggestion.symbol);
    setShowSuggestions(false);
    setFilteredSuggestions([]);
  };

  // Handle ticker input blur with smart formatting
  const handleTickerBlur = () => {
    setTimeout(() => {
      setShowSuggestions(false);
      if (ticker.trim()) {
        const formatted = formatIndianTicker(ticker);
        if (formatted !== ticker) {
          setTicker(formatted);
        }
      }
    }, 200);
  };

  // Handle ticker input focus
  const handleTickerFocus = () => {
    const suggestions = filterIndianSuggestions(ticker);
    setFilteredSuggestions(suggestions);
    setShowSuggestions(true);
  };

  // Get sector color
  const getSectorColor = (sector: string) => {
    const colors: { [key: string]: string } = {
      'Banking': 'bg-blue-500/20 text-blue-300',
      'IT Services': 'bg-green-500/20 text-green-300',
      'FMCG': 'bg-purple-500/20 text-purple-300',
      'Auto': 'bg-red-500/20 text-red-300',
      'Pharma': 'bg-cyan-500/20 text-cyan-300',
      'Oil & Gas': 'bg-orange-500/20 text-orange-300',
      'Telecom': 'bg-pink-500/20 text-pink-300',
      'Steel': 'bg-gray-500/20 text-gray-300',
      'Cement': 'bg-yellow-500/20 text-yellow-300',
      'Power': 'bg-indigo-500/20 text-indigo-300'
    };
    return colors[sector] || 'bg-gray-500/20 text-gray-300';
  };

  const fetchCompanyData = async (tickerSymbol: string): Promise<CompanyData> => {
    try {
      const response = await fetch(API_ENDPOINTS.getCompanyInfo, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ticker: tickerSymbol }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch company data');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching company data:', error);
      throw error;
    }
  };

  const handleFetchData = async () => {
    if (!ticker.trim()) return;
    
    setIsLoading(true);
    try {
      const data = await fetchCompanyData(ticker);
      setCompanyData(data);
      
      // Auto-populate DCF inputs with 3-year data
      setDCFInputs(prev => ({
        ...prev,
        revenueGrowthRate: data.historicalData.revenueGrowth3Y,
        fcfMargin: data.historicalData.fcfMargin3Y
      }));
      
      setCurrentStep(2);
    } catch (error) {
      console.error('Error fetching data:', error);
      alert(`Error fetching data: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsLoading(false);
    }
  };

  const calculateDCF = async () => {
    if (!companyData) return;

    try {
      const response = await fetch(API_ENDPOINTS.calculateDCF, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ticker: companyData.ticker,
          revenueGrowthRate: dcfInputs.revenueGrowthRate,
          fcfMargin: dcfInputs.fcfMargin,
          numberOfYears: dcfInputs.numberOfYears,
          discountRate: dcfInputs.discountRate,
          terminalGrowthRate: dcfInputs.terminalGrowthRate
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to calculate DCF');
      }

      const calculatedResults: DCFResults = await response.json();
      setResults(calculatedResults);
      setCurrentStep(3);
    } catch (error) {
      console.error('Error calculating DCF:', error);
      alert(`Error calculating DCF: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  // Navigation functions
  const goToStep = (step: number) => {
    if (step === 1) {
      setCurrentStep(1);
    } else if (step === 2 && companyData) {
      setCurrentStep(2);
    } else if (step === 3 && results) {
      setCurrentStep(3);
    }
  };

  const resetCalculator = () => {
    setCurrentStep(1);
    setTicker('');
    setCompanyData(null);
    setResults(null);
    setDCFInputs({
      revenueGrowthRate: 0,
      fcfMargin: 0,
      numberOfYears: 7,
      discountRate: 10,
      terminalGrowthRate: 6
    });
  };

  const Tooltip = ({ id, title, content }: { id: string; title: string; content: string }) => (
    <div className="relative inline-block">
      <button
        onMouseEnter={() => setShowTooltip(id)}
        onMouseLeave={() => setShowTooltip(null)}
        className="ml-2 text-blue-400 hover:text-blue-300 transition-colors"
      >
        <HelpCircle className="w-4 h-4" />
      </button>
      {showTooltip === id && (
        <div className={`absolute z-50 w-80 p-4 rounded-xl shadow-2xl border left-1/2 transform -translate-x-1/2 bottom-full mb-2 ${isDarkMode ? 'bg-gray-800/98 backdrop-blur-xl border-gray-700/50' : 'bg-white/98 backdrop-blur-xl border-gray-200/50'}`}>
          <h4 className="font-bold text-sm mb-2 text-blue-400">{title}</h4>
          <p className={`text-xs leading-relaxed ${isDarkMode ? 'text-gray-200' : 'text-gray-700'}`}>{content}</p>
          <div className={`absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent ${isDarkMode ? 'border-t-gray-800' : 'border-t-white'}`}></div>
        </div>
      )}
    </div>
  );

  const themeClasses = isDarkMode 
    ? 'bg-gradient-to-br from-gray-900 via-slate-900 to-gray-900 text-white' 
    : 'bg-gradient-to-br from-blue-50 via-white to-indigo-50 text-gray-900';
  
  const cardClasses = isDarkMode 
    ? 'bg-gray-800/40 backdrop-blur-xl border-gray-700/50' 
    : 'bg-white/60 backdrop-blur-xl border-gray-200/50';
  
  const inputClasses = isDarkMode 
    ? 'bg-gray-700/50 border-gray-600/50 text-white placeholder-gray-400 focus:bg-gray-700/70' 
    : 'bg-white/70 border-gray-300/50 text-gray-900 placeholder-gray-500 focus:bg-white/90';

  // Helper function to format large numbers with proper currency
  const formatCurrency = (value: number, currency: string, type: 'marketCap' | 'revenue' | 'shares') => {
    if (currency === 'INR') {
      if (type === 'marketCap' || type === 'revenue') {
        return `₹${value.toLocaleString()} Cr`;
      } else if (type === 'shares') {
        return `${value.toLocaleString()} Cr`;
      }
    } else if (currency === 'USD') {
      if (type === 'marketCap' || type === 'revenue') {
        return `$${value.toLocaleString()}B`;
      } else if (type === 'shares') {
        return `${value.toLocaleString()}B`;
      }
    }
    return value.toLocaleString();
  };

  return (
    <div className={`min-h-screen transition-all duration-500 ${themeClasses}`}>
      <div className="container mx-auto px-6 py-8 max-w-7xl">
        {/* Header */}
        <div className="flex justify-between items-center mb-12">
          <div className="flex items-center space-x-4">
            <div className="p-4 bg-gradient-to-r from-blue-500 to-purple-600 rounded-3xl shadow-2xl">
              <Calculator className="w-10 h-10 text-white" />
            </div>
            <div>
              <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                DCF Calculator
              </h1>
              <p className="text-lg opacity-70 mt-2">Warren Buffett Style Valuation Tool</p>
              <p className="text-sm opacity-60 mt-1 flex items-center">
                <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                Currently supports Indian Stock Markets
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <button
              onClick={resetCalculator}
              className={`px-6 py-3 rounded-xl border transition-all duration-300 ${cardClasses} border hover:scale-105 shadow-lg font-medium`}
            >
              Reset
            </button>
            <button
              onClick={() => setIsDarkMode(!isDarkMode)}
              className={`flex items-center space-x-2 px-6 py-3 rounded-xl border transition-all duration-300 ${cardClasses} border hover:scale-105 shadow-lg`}
            >
              {isDarkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
              <span className="font-medium">{isDarkMode ? 'Light' : 'Dark'}</span>
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex justify-center mb-8">
          <div className={`flex rounded-2xl p-2 ${cardClasses} border`}>
            <button
              onClick={() => setActiveTab('single')}
              className={`px-8 py-3 rounded-xl font-medium transition-all duration-300 ${
                activeTab === 'single'
                  ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg'
                  : 'text-gray-500 hover:text-gray-300'
              }`}
            >
              Single Stock Analysis
            </button>
            <button
              onClick={() => setActiveTab('bulk')}
              className={`px-8 py-3 rounded-xl font-medium transition-all duration-300 ${
                activeTab === 'bulk'
                  ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg'
                  : 'text-gray-500 hover:text-gray-300'
              }`}
            >
              Bulk Mode
            </button>
          </div>
        </div>

        {/* Bulk Mode Coming Soon */}
        {activeTab === 'bulk' && (
          <div className="max-w-2xl mx-auto">
            <div className={`p-12 rounded-3xl border shadow-2xl ${cardClasses} text-center`}>
              <div className="w-24 h-24 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-6">
                <BarChart3 className="w-12 h-12 text-white" />
              </div>
              <h2 className="text-4xl font-bold mb-4">Bulk Mode</h2>
              <p className="text-xl opacity-70 mb-6">Analyze multiple stocks simultaneously</p>
              <div className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-yellow-500/20 to-orange-500/20 rounded-xl border border-yellow-500/30">
                <span className="text-yellow-500 font-semibold">Coming Soon</span>
              </div>
            </div>
          </div>
        )}

        {/* Progress Steps */}
        {activeTab === 'single' && (
          <div className="mb-8">
            <div className="flex justify-center mb-6">
              <div className="flex items-center space-x-12">
                {[
                  { step: 1, title: 'Enter Ticker', icon: Search },
                  { step: 2, title: 'Review Data & Parameters', icon: TrendingUp },
                  { step: 3, title: 'View Results', icon: Calculator }
                ].map(({ step, title, icon: Icon }) => (
                  <div key={step} className="flex items-center">
                    <div className="text-center">
                      <div 
                        onClick={() => goToStep(step)}
                        className={`w-16 h-16 rounded-full flex items-center justify-center font-bold text-lg transition-all duration-300 mb-3 cursor-pointer hover:scale-110 ${
                          currentStep >= step 
                            ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg hover:shadow-xl' 
                            : `${isDarkMode ? 'bg-gray-700 text-gray-400 hover:bg-gray-600' : 'bg-gray-200 text-gray-500 hover:bg-gray-300'} ${
                              (step === 2 && !companyData) || (step === 3 && !results) ? 'cursor-not-allowed opacity-50 hover:scale-100' : ''
                            }`
                        }`}
                        title={
                          (step === 2 && !companyData) ? 'Complete step 1 first' :
                          (step === 3 && !results) ? 'Complete step 2 first' :
                          `Go to ${title}`
                        }
                      >
                        <Icon className="w-6 h-6" />
                      </div>
                      <p className={`text-sm font-medium min-w-[120px] ${currentStep >= step ? 'text-blue-400' : 'text-gray-500'}`}>
                        {title}
                      </p>
                    </div>
                    {step < 3 && (
                      <ArrowRight className={`w-6 h-6 mx-8 transition-all duration-300 ${
                        currentStep > step ? 'text-blue-500' : 'text-gray-400'
                      }`} />
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Progress Bar */}
        {activeTab === 'single' && (
          <div className="mb-8">
            <div className={`w-full h-2 rounded-full ${isDarkMode ? 'bg-gray-700' : 'bg-gray-200'} overflow-hidden`}>
              <div 
                className="h-full bg-gradient-to-r from-blue-500 to-purple-600 transition-all duration-500 ease-out"
                style={{ width: `${(currentStep / 3) * 100}%` }}
              ></div>
            </div>
            <div className="flex justify-between text-xs opacity-60 mt-2">
              <span>Start</span>
              <span>{currentStep}/3</span>
              <span>Complete</span>
            </div>
          </div>
        )}

        {/* Step 1: Ticker Input */}
        {activeTab === 'single' && currentStep === 1 && (
          <div className="max-w-2xl mx-auto">
            <div className={`p-8 rounded-3xl border shadow-2xl ${cardClasses}`}>
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold mb-2">Enter Indian Stock Ticker</h2>
                <p className="text-lg opacity-70">Search from 500+ NSE listed companies</p>
              </div>
              
              <div className="space-y-6">
                <div className="relative">
                  <label className="block text-lg font-medium mb-3 opacity-80 flex items-center">
                    Stock Ticker Symbol
                    <Tooltip 
                      id="ticker"
                      title="Stock Ticker Symbol"
                      content="Enter the stock symbol as listed on NSE. Examples: TCS for Tata Consultancy Services, RELIANCE for Reliance Industries, INFY for Infosys. You can also type company names."
                    />
                  </label>
                  <div className="relative">
                    <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                      type="text"
                      value={ticker}
                      onChange={handleTickerChange}
                      onFocus={handleTickerFocus}
                      onBlur={handleTickerBlur}
                      className={`w-full pl-12 pr-16 py-4 text-xl rounded-2xl border-2 focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 transition-all ${inputClasses}`}
                      placeholder="Type company name or symbol (e.g., Reliance, TCS, HDFC)"
                      onKeyPress={(e) => e.key === 'Enter' && handleFetchData()}
                      autoComplete="off"
                    />
                    <div className="absolute right-4 top-1/2 transform -translate-y-1/2 flex items-center space-x-2">
                      <span className="text-xs px-2 py-1 bg-orange-500/20 text-orange-300 rounded-full font-medium">NSE</span>
                      <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${showSuggestions ? 'rotate-180' : ''}`} />
                    </div>
                  </div>

                  {/* Enhanced Suggestions Dropdown */}
                  {showSuggestions && filteredSuggestions.length > 0 && (
                    <div className={`absolute top-full left-0 right-0 mt-2 rounded-2xl border shadow-2xl z-50 max-h-96 overflow-y-auto ${isDarkMode ? 'bg-gray-800/95 backdrop-blur-xl border-gray-700/50' : 'bg-white/95 backdrop-blur-xl border-gray-200/50'}`}>
                      <div className="p-2">
                        <div className="text-xs text-gray-400 mb-2 px-2">
                          {filteredSuggestions.length} companies found
                        </div>
                        {filteredSuggestions.map((suggestion) => (
                          <button
                            key={suggestion.symbol}
                            onClick={() => handleSuggestionSelect(suggestion)}
                            className={`w-full px-3 py-3 text-left transition-colors rounded-lg mb-1 group ${isDarkMode ? 'hover:bg-gray-700/70' : 'hover:bg-gray-100/70'}`}
                          >
                            <div className="flex justify-between items-start">
                              <div className="flex-1 min-w-0">
                                <div className="flex items-center space-x-2 mb-1">
                                  <span className={`font-medium transition-colors ${isDarkMode ? 'text-white group-hover:text-blue-400' : 'text-gray-900 group-hover:text-blue-600'}`}>
                                    {suggestion.symbol.replace('.NS', '')}
                                  </span>
                                  <span className={`text-xs px-2 py-0.5 rounded-full ${getSectorColor(suggestion.sector)}`}>
                                    {suggestion.sector}
                                  </span>
                                </div>
                                <div className={`text-sm truncate ${isDarkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                                  {suggestion.name}
                                </div>
                              </div>
                              <div className={`text-xs ml-2 ${isDarkMode ? 'text-gray-500' : 'text-gray-400'}`}>
                                {suggestion.mcap}
                              </div>
                            </div>
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
                
                <button
                  onClick={handleFetchData}
                  disabled={!ticker.trim() || isLoading}
                  className="w-full py-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-2xl font-bold text-lg hover:shadow-2xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-6 h-6 animate-spin" />
                      <span>Fetching Data...</span>
                    </>
                  ) : (
                    <>
                      <Search className="w-6 h-6" />
                      <span>Analyze Stock</span>
                    </>
                  )}
                </button>
                
                {/* Popular Indian Stocks by Sector */}
                <div className="mt-8 space-y-4">
                  <h3 className="text-sm font-medium text-gray-400">Popular Stocks by Sector</h3>
                  
                  {/* Banking */}
                  <div>
                    <h4 className="text-xs text-blue-300 mb-2 flex items-center">
                      <div className="w-2 h-2 bg-blue-500 rounded-full mr-2"></div>
                      Banking
                    </h4>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                      {POPULAR_INDIAN_STOCKS.filter(s => s.sector === 'Banking').slice(0, 4).map((stock) => (
                        <button
                          key={stock.symbol}
                          onClick={() => handleSuggestionSelect(stock)}
                          className="px-3 py-2 bg-blue-500/10 hover:bg-blue-500/20 rounded-lg text-sm transition-colors border border-blue-500/20 hover:border-blue-500/40"
                        >
                          <div className="font-medium">{stock.symbol.replace('.NS', '')}</div>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* IT Services */}
                  <div>
                    <h4 className="text-xs text-green-300 mb-2 flex items-center">
                      <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                      IT Services
                    </h4>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                      {POPULAR_INDIAN_STOCKS.filter(s => s.sector === 'IT Services').slice(0, 4).map((stock) => (
                        <button
                          key={stock.symbol}
                          onClick={() => handleSuggestionSelect(stock)}
                          className="px-3 py-2 bg-green-500/10 hover:bg-green-500/20 rounded-lg text-sm transition-colors border border-green-500/20 hover:border-green-500/40"
                        >
                          <div className="font-medium">{stock.symbol.replace('.NS', '')}</div>
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Other Popular */}
                  <div>
                    <h4 className="text-xs text-gray-300 mb-2 flex items-center">
                      <div className="w-2 h-2 bg-gray-500 rounded-full mr-2"></div>
                      Other Popular
                    </h4>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                      {['RELIANCE.NS', 'ITC.NS', 'BHARTIARTL.NS', 'MARUTI.NS'].map((symbol) => {
                        const stock = POPULAR_INDIAN_STOCKS.find(s => s.symbol === symbol);
                        return stock ? (
                          <button
                            key={symbol}
                            onClick={() => handleSuggestionSelect(stock)}
                            className="px-3 py-2 bg-purple-500/10 hover:bg-purple-500/20 rounded-lg text-sm transition-colors border border-purple-500/20 hover:border-purple-500/40"
                          >
                            <div className="font-medium">{symbol.replace('.NS', '')}</div>
                          </button>
                        ) : null;
                      })}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Step 2: Company Data & DCF Inputs */}
        {activeTab === 'single' && currentStep === 2 && companyData && (
          <div className="space-y-8">
            {/* Company Information - Full Width */}
            <div className={`p-8 rounded-3xl border shadow-2xl ${cardClasses}`}>
              <h2 className="text-3xl font-bold mb-6 flex items-center justify-center">
                <BarChart3 className="w-8 h-8 text-blue-500 mr-3" />
                {companyData.name} ({companyData.ticker})
              </h2>
              
              {/* Key Metrics Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
                <div className="text-center p-4 bg-gradient-to-br from-blue-500/10 to-purple-500/10 rounded-2xl">
                  <p className="text-sm opacity-70 mb-2">Current Price</p>
                  <p className="text-2xl font-bold text-blue-500">₹{companyData.currentPrice.toFixed(2)}</p>
                </div>
                <div className="text-center p-4 bg-gradient-to-br from-green-500/10 to-blue-500/10 rounded-2xl">
                  <p className="text-sm opacity-70 mb-2">Market Cap</p>
                  <p className="text-2xl font-bold text-green-500">
                    {companyData.marketCap ? formatCurrency(companyData.marketCap, companyData.currency, 'marketCap') : 'N/A'}
                  </p>
                </div>
                <div className="text-center p-4 bg-gradient-to-br from-purple-500/10 to-pink-500/10 rounded-2xl">
                  <p className="text-sm opacity-70 mb-2">Last Yearly Revenue</p>
                  <p className="text-2xl font-bold text-purple-500">{formatCurrency(companyData.lastYearlyRevenue, companyData.currency, 'revenue')}</p>
                </div>
                <div className="text-center p-4 bg-gradient-to-br from-orange-500/10 to-red-500/10 rounded-2xl">
                  <p className="text-sm opacity-70 mb-2">Shares Outstanding</p>
                  <p className="text-2xl font-bold text-orange-500">{formatCurrency(companyData.totalSharesOut, companyData.currency, 'shares')}</p>
                </div>
              </div>

              {/* Historical Data Table */}
              <div className="mb-8">
                <h3 className="text-2xl font-bold mb-6 text-center">Historical Performance</h3>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b-2 border-gray-600/30">
                        <th className="text-left py-4 font-bold text-lg"></th>
                        <th className="text-center py-4 font-bold text-lg">3 year avg</th>
                        <th className="text-center py-4 font-bold text-lg">2 year avg</th>
                        <th className="text-center py-4 font-bold text-lg">1 year</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr>
                        <td className="py-4 font-semibold text-lg">Revenue Growth</td>
                        <td className="text-center py-4 text-green-500 font-bold text-lg">{companyData.historicalData.revenueGrowth3Y}%</td>
                        <td className="text-center py-4 font-semibold text-lg">{companyData.historicalData.revenueGrowth2Y}%</td>
                        <td className="text-center py-4 font-semibold text-lg">{companyData.historicalData.revenueGrowth1Y}%</td>
                      </tr>
                      <tr>
                        <td className="py-4 font-semibold text-lg">Dilution(+)/Buybacks(-)</td>
                        <td className="text-center py-4 text-green-500 font-bold text-lg">{companyData.historicalData.dilution3Y}%</td>
                        <td className="text-center py-4 font-semibold text-lg">{companyData.historicalData.dilution2Y}%</td>
                        <td className="text-center py-4 font-semibold text-lg">{companyData.historicalData.dilution1Y}%</td>
                      </tr>
                      <tr>
                        <td className="py-4 font-semibold text-lg">FCF Margins</td>
                        <td className="text-center py-4 text-blue-500 font-bold text-lg">{companyData.historicalData.fcfMargin3Y}%</td>
                        <td className="text-center py-4 font-semibold text-lg">{companyData.historicalData.fcfMargin2Y}%</td>
                        <td className="text-center py-4 font-semibold text-lg">{companyData.historicalData.fcfMargin1Y}%</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            {/* DCF Inputs */}
            <div className={`p-8 rounded-3xl border shadow-2xl ${cardClasses}`}>
              <h2 className="text-3xl font-bold mb-2 flex items-center justify-center">
                <TrendingUp className="w-8 h-8 text-green-500 mr-3" />
                Set Your DCF Parameters
              </h2>
              <p className="text-center text-lg opacity-70 mb-8">Adjust these values based on your analysis (pre-filled with 3-year averages)</p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="space-y-6">
                  <div className="p-6 bg-gradient-to-br from-green-500/10 to-blue-500/10 rounded-2xl">
                    <label className="block text-lg font-bold mb-3 text-green-500 flex items-center">
                      Revenue Growth Rate (%)
                      <Tooltip 
                        id="revenue-growth"
                        title="Revenue Growth Rate"
                        content="The expected annual revenue growth rate for the company. This is pre-filled with the 3-year historical average. Consider the company's market position, industry trends, and competitive advantages when adjusting this value."
                      />
                    </label>
                    <input
                      type="number"
                      value={dcfInputs.revenueGrowthRate}
                      onChange={(e) => setDCFInputs(prev => ({ ...prev, revenueGrowthRate: parseFloat(e.target.value) || 0 }))}
                      className={`w-full px-6 py-4 text-xl rounded-xl border-2 focus:ring-4 focus:ring-green-500/20 focus:border-green-500 transition-all ${inputClasses}`}
                      step="0.01"
                    />
                    <p className="text-sm opacity-70 mt-2">Using 3-year average: {companyData.historicalData.revenueGrowth3Y}%</p>
                  </div>
                  
                  <div className="p-6 bg-gradient-to-br from-blue-500/10 to-purple-500/10 rounded-2xl">
                    <label className="block text-lg font-bold mb-3 text-blue-500 flex items-center">
                      Free Cash Flow Margin (%)
                      <Tooltip 
                        id="fcf-margin"
                        title="Free Cash Flow Margin"
                        content="The percentage of revenue that converts to free cash flow. This represents the company's ability to generate cash after necessary capital expenditures. Pre-filled with 3-year historical average."
                      />
                    </label>
                    <input
                      type="number"
                      value={dcfInputs.fcfMargin}
                      onChange={(e) => setDCFInputs(prev => ({ ...prev, fcfMargin: parseFloat(e.target.value) || 0 }))}
                      className={`w-full px-6 py-4 text-xl rounded-xl border-2 focus:ring-4 focus:ring-blue-500/20 focus:border-blue-500 transition-all ${inputClasses}`}
                      step="0.01"
                    />
                    <p className="text-sm opacity-70 mt-2">Using 3-year average: {companyData.historicalData.fcfMargin3Y}%</p>
                  </div>
                  
                  <div className="p-6 bg-gradient-to-br from-purple-500/10 to-pink-500/10 rounded-2xl">
                    <label className="block text-lg font-bold mb-3 text-purple-500 flex items-center">
                      Number of Years
                      <Tooltip 
                        id="years"
                        title="Projection Period"
                        content="The number of years to project future cash flows. Warren Buffett typically uses 7-10 years. Longer periods increase uncertainty but capture more of the company's growth potential."
                      />
                    </label>
                    <input
                      type="number"
                      value={dcfInputs.numberOfYears}
                      onChange={(e) => setDCFInputs(prev => ({ ...prev, numberOfYears: parseInt(e.target.value) || 7 }))}
                      className={`w-full px-6 py-4 text-xl rounded-xl border-2 focus:ring-4 focus:ring-purple-500/20 focus:border-purple-500 transition-all ${inputClasses}`}
                      min="1"
                      max="20"
                    />
                    <p className="text-sm opacity-70 mt-2">Default: 7 years (Warren Buffett's typical horizon)</p>
                  </div>
                </div>
                
                <div className="space-y-6">
                  <div className="p-6 bg-gradient-to-br from-red-500/10 to-orange-500/10 rounded-2xl">
                    <label className="block text-lg font-bold mb-3 text-red-500 flex items-center">
                      Discount Rate / WACC (%)
                      <Tooltip 
                        id="discount-rate"
                        title="Discount Rate (WACC)"
                        content="The rate used to discount future cash flows to present value. This should reflect the company's cost of capital and investment risk. Warren Buffett often uses 10% as a conservative estimate."
                      />
                    </label>
                    <input
                      type="number"
                      value={dcfInputs.discountRate}
                      onChange={(e) => setDCFInputs(prev => ({ ...prev, discountRate: parseFloat(e.target.value) || 10 }))}
                      className={`w-full px-6 py-4 text-xl rounded-xl border-2 focus:ring-4 focus:ring-red-500/20 focus:border-red-500 transition-all ${inputClasses}`}
                      step="0.1"
                    />
                    <p className="text-sm opacity-70 mt-2">Default: 10% (Conservative estimate)</p>
                  </div>
                  
                  <div className="p-6 bg-gradient-to-br from-yellow-500/10 to-orange-500/10 rounded-2xl">
                    <label className="block text-lg font-bold mb-3 text-yellow-500 flex items-center">
                      Terminal Growth Rate (%)
                      <Tooltip 
                        id="terminal-growth"
                        title="Terminal Growth Rate"
                        content="The expected long-term growth rate beyond the projection period. This should not exceed the long-term GDP growth rate (typically 2-4%). Conservative estimates are preferred."
                      />
                    </label>
                    <input
                      type="number"
                      value={dcfInputs.terminalGrowthRate}
                      onChange={(e) => setDCFInputs(prev => ({ ...prev, terminalGrowthRate: parseFloat(e.target.value) || 6 }))}
                      className={`w-full px-6 py-4 text-xl rounded-xl border-2 focus:ring-4 focus:ring-yellow-500/20 focus:border-yellow-500 transition-all ${inputClasses}`}
                      step="0.1"
                    />
                    <p className="text-sm opacity-70 mt-2">Default: 6% (Long-term GDP growth for India)</p>
                  </div>
                  
                  <div className="flex items-center justify-center h-full">
                    <button
                      onClick={calculateDCF}
                      className="w-full py-6 bg-gradient-to-r from-green-500 to-blue-600 text-white rounded-2xl font-bold text-2xl hover:shadow-2xl transition-all duration-300 flex items-center justify-center space-x-3"
                    >
                      <Calculator className="w-8 h-8" />
                      <span>Calculate Fair Value</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Step 3: Results */}
        {activeTab === 'single' && currentStep === 3 && results && companyData && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Main Results */}
            <div className={`p-8 rounded-3xl border shadow-2xl ${cardClasses}`}>
              <h2 className="text-2xl font-bold mb-6 flex items-center">
                <DollarSign className="w-7 h-7 text-green-500 mr-3" />
                Valuation Results
              </h2>
              
              <div className="space-y-6">
                <div className="text-center p-6 bg-gradient-to-r from-green-500/20 to-blue-500/20 rounded-2xl">
                  <p className="text-sm opacity-70 mb-2">Fair Value</p>
                  <p className="text-5xl font-bold text-green-500">₹{results.fairValue.toFixed(2)}</p>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-4 bg-gray-500/10 rounded-xl">
                    <p className="text-sm opacity-70 mb-1">Current Price</p>
                    <p className="text-2xl font-bold">₹{results.currentPrice.toFixed(2)}</p>
                  </div>
                  <div className="text-center p-4 bg-gray-500/10 rounded-xl">
                    <p className="text-sm opacity-70 mb-1">Upside/Downside</p>
                    <p className={`text-2xl font-bold ${results.upsideDownside > 0 ? 'text-green-500' : 'text-red-500'}`}>
                      {results.upsideDownside > 0 ? '+' : ''}{results.upsideDownside.toFixed(1)}%
                    </p>
                  </div>
                </div>
                
                <div className="text-center">
                  {results.upsideDownside > 20 ? (
                    <div className="p-4 bg-green-500/20 rounded-xl border border-green-500/30">
                      <p className="text-green-500 font-bold text-xl">Strong Buy</p>
                      <p className="text-sm opacity-80 mt-1">Significant undervaluation detected</p>
                    </div>
                  ) : results.upsideDownside > 0 ? (
                    <div className="p-4 bg-blue-500/20 rounded-xl border border-blue-500/30">
                      <p className="text-blue-500 font-bold text-xl">Buy</p>
                      <p className="text-sm opacity-80 mt-1">Moderately undervalued</p>
                    </div>
                  ) : results.upsideDownside > -20 ? (
                    <div className="p-4 bg-yellow-500/20 rounded-xl border border-yellow-500/30">
                      <p className="text-yellow-500 font-bold text-xl">Hold</p>
                      <p className="text-sm opacity-80 mt-1">Fairly valued</p>
                    </div>
                  ) : (
                    <div className="p-4 bg-red-500/20 rounded-xl border border-red-500/30">
                      <p className="text-red-500 font-bold text-xl">Avoid</p>
                      <p className="text-sm opacity-80 mt-1">Overvalued</p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Additional Analysis */}
            <div className={`p-8 rounded-3xl border shadow-2xl ${cardClasses}`}>
              <h2 className="text-2xl font-bold mb-6">Sensitivity Analysis</h2>
              
              <div className="space-y-6">
                <div>
                  <p className="text-lg font-semibold mb-4">Yearly Revenue After {dcfInputs.numberOfYears} Years:</p>
                  <p className="text-3xl font-bold text-blue-500">{formatCurrency(results.yearlyRevenueAfterNYears, companyData.currency, 'revenue')}</p>
                </div>
                
                <div className="border-t border-gray-600/30 pt-6">
                  <p className="text-lg font-semibold mb-4">To Justify Current Price of ₹{results.currentPrice.toFixed(2)}:</p>
                  
                  <div className="space-y-4">
                    <div className="flex justify-between items-center p-3 bg-gray-500/10 rounded-xl">
                      <span className="text-sm opacity-80">Required Revenue Growth at Current FCF Margin:</span>
                      <span className="font-bold text-lg">{results.requiredRevenueGrowth.toFixed(2)}%</span>
                    </div>
                    
                    <div className="text-center text-sm opacity-60">Or</div>
                    
                    <div className="flex justify-between items-center p-3 bg-gray-500/10 rounded-xl">
                      <span className="text-sm opacity-80">Required FCF Margin at Current Revenue Growth:</span>
                      <span className="font-bold text-lg">{results.requiredFCFMargin.toFixed(2)}%</span>
                    </div>
                    
                    <div className="text-center text-sm opacity-60">Or</div>
                    
                    <div className="flex justify-between items-center p-3 bg-gray-500/10 rounded-xl">
                      <span className="text-sm opacity-80">Compounded Return Rate for {dcfInputs.numberOfYears} Years:</span>
                      <span className="font-bold text-lg">{results.compoundedReturnRate.toFixed(2)}%</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Quick Tips - Only visible on Step 1 */}
        <div className="mt-12 max-w-4xl mx-auto">
          {activeTab === 'single' && currentStep === 1 && (
            <div className={`p-4 rounded-2xl border ${cardClasses}`}>
              <div className="flex items-start space-x-3">
                <Info className="w-5 h-5 text-blue-400 mt-0.5 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold text-blue-400 mb-1">Quick Tip</h3>
                  <p className="text-sm opacity-80">
                    Enter any Indian stock ticker symbol (e.g., TCS, RELIANCE, INFY) to get started with your DCF analysis.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DCFCalculator;