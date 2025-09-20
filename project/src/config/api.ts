// API Configuration for different environments

const isDevelopment = import.meta.env.DEV;

export const API_BASE_URL = isDevelopment 
  ? 'http://localhost:8000'  // Development server
  : '';  // Production: same domain as the frontend

export const API_ENDPOINTS = {
  GET_COMPANY_INFO: `${API_BASE_URL}/api/get_company_info`,
  CALCULATE_DCF: `${API_BASE_URL}/api/calculate_dcf`,
} as const;
