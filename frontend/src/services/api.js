import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error);
    if (error.response?.status === 500) {
      console.error('Server error:', error.response.data);
    }
    return Promise.reject(error);
  }
);

export const analysisAPI = {
  // Create new analysis
  createAnalysis: (data) => {
    if (data.uploaded_file) {
      // File upload
      const formData = new FormData();
      formData.append('title', data.title);
      formData.append('uploaded_file', data.uploaded_file);
      return api.post('/analysis/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
    } else {
      // Text input
      return api.post('/analysis/', data);
    }
  },

  // Get all analyses
  getAnalyses: () => api.get('/analysis/'),

  // Get specific analysis
  getAnalysis: (id) => api.get(`/analysis/${id}/`),

  // ✅ NEW: Get analysis status
  getAnalysisStatus: (id) => api.get(`/analysis/${id}/status/`),

  // Download report
  downloadReport: (id) => api.get(`/analysis/${id}/download_report/`, {
    responseType: 'blob',
  }),

  // Get analysis statistics
  getStats: () => api.get('/analysis/analysis_stats/'),
};

export default api;