import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response.data,
      (error) => {
        const message = error.response?.data?.detail || error.message || 'An error occurred';
        throw new Error(message);
      }
    );
  }

  async processRequirements(data) {
    return this.client.post('/api/process-requirements', data);
  }

  async generateDiagrams(data) {
    return this.client.post('/api/generate-diagrams', data);
  }

  async getComparisonStats() {
    return this.client.get('/api/comparison-stats');
  }

  async getCaseStudies() {
    return this.client.get('/api/case-studies');
  }

  async getCaseStudy(id) {
    return this.client.get(`/api/case-studies/${id}`);
  }

  async uploadFile(formData, onUploadProgress) {
    return this.client.post('/api/upload-file', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    });
  }

  async exportResearchData() {
    return this.client.get('/api/export-data');
  }

  async clearAllData() {
    return this.client.delete('/api/clear-data');
  }

  // Health check
  async healthCheck() {
    return this.client.get('/');
  }
}

export const apiService = new ApiService();
