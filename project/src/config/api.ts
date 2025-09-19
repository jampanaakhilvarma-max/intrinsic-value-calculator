// API Configuration
const getApiBaseUrl = () => {
  // In production, use the same origin (Railway will serve both frontend and backend)
  if (import.meta.env.PROD) {
    return window.location.origin;
  }
  
  // In development, use localhost
  return 'http://localhost:8000';
};

export const API_BASE_URL = getApiBaseUrl();

export const API_ENDPOINTS = {
  getCompanyInfo: `${API_BASE_URL}/api/get_company_info`,
  calculateDCF: `${API_BASE_URL}/api/calculate_dcf`,
} as const;