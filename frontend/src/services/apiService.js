import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes for AI processing
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Response Error:', error);
    
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.detail || error.response.data?.message || 'Server Error';
      throw new Error(`${error.response.status}: ${message}`);
    } else if (error.request) {
      // Request made but no response
      throw new Error('No response from server. Please check if the backend is running.');
    } else {
      // Something else happened
      throw new Error(error.message || 'Unknown error occurred');
    }
  }
);

export const apiService = {
  async processRequirements(data) {
    try {
      const response = await apiClient.post('/process-requirements', data);
      return response.data;
    } catch (error) {
      throw new Error(`Requirements processing failed: ${error.message}`);
    }
  },

  async generateDiagrams(data) {
    try {
      const response = await apiClient.post('/generate-diagrams', data);
      return response.data;
    } catch (error) {
      throw new Error(`Diagram generation failed: ${error.message}`);
    }
  },

  async uploadFile(formData, onUploadProgress) {
    try {
      const response = await apiClient.post('/upload-file', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress,
        timeout: 60000 // 1 minute for file upload
      });
      return response.data;
    } catch (error) {
      throw new Error(`File upload failed: ${error.message}`);
    }
  },

  async validateRequirement(requirement) {
    try {
      const response = await apiClient.post('/validate-requirement', { requirement });
      return response.data;
    } catch (error) {
      throw new Error(`Requirement validation failed: ${error.message}`);
    }
  },

  async verifyDiagram(data) {
    try {
      const response = await apiClient.post('/verify-diagram', data);
      return response.data;
    } catch (error) {
      throw new Error(`Diagram verification failed: ${error.message}`);
    }
  },

  async optimizeDiagram(data) {
    try {
      const response = await apiClient.post('/optimize-diagram', data);
      return response.data;
    } catch (error) {
      throw new Error(`Diagram optimization failed: ${error.message}`);
    }
  },

  async generateBothDiagrams(data) {
    try {
      const response = await apiClient.post('/generate-both-diagrams', data);
      return response.data;
    } catch (error) {
      throw new Error(`Simultaneous diagram generation failed: ${error.message}`);
    }
  },

  async identifyActors(data) {
    try {
      const response = await apiClient.post('/identify-actors', data);
      return response.data;
    } catch (error) {
      throw new Error(`Actor identification failed: ${error.message}`);
    }
  },

  async finalOptimization(data) {
    try {
      console.log('Final optimization request data:', data);
      const response = await apiClient.post('/final-optimization', data);
      return response.data;
    } catch (error) {
      console.error('Final optimization error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        requestData: data
      });
      throw new Error(`Final optimization failed: ${error.message}`);
    }
  },

  async getComparisonStats() {
    const response = await axios.get(`${API_BASE_URL}/comparison-stats`);
    return response.data;
  },

  async getCaseStudies() {
    const response = await axios.get(`${API_BASE_URL}/case-studies`);
    return response.data;
  },

  async getCaseStudy(id) {
    const response = await axios.get(`${API_BASE_URL}/case-studies/${id}`);
    return response.data;
  },

  async exportResearchData() {
    const response = await axios.get(`${API_BASE_URL}/export-research-data`);
    return response.data;
  },

  async clearData() {
    const response = await axios.delete(`${API_BASE_URL}/clear-data`);
    return response.data;
  },

  // Report PlantUML rendering errors to backend for analysis
  async reportPlantUMLError(data) {
    try {
      const response = await apiClient.post('/report-plantuml-error', data);
      return response.data;
    } catch (error) {
      console.error('Failed to report PlantUML error:', error.message);
      // Don't throw error here as this is just reporting
      return null;
    }
  },

  // Validate PlantUML syntax before rendering
  async validatePlantUMLSyntax(data) {
    try {
      const response = await apiClient.post('/validate-plantuml', data);
      return response.data;
    } catch (error) {
      throw new Error(`PlantUML validation failed: ${error.message}`);
    }
  },

  // Analyze AI vs RUPP SNL detailed comparison
  async analyzeAIvsRUPP(data) {
    try {
      const response = await apiClient.post('/analyze-ai-snl-detailed', data);
      return response.data;
    } catch (error) {
      console.error('AI vs RUPP analysis failed:', error);
      throw error;
    }
  },

  // Generate Java code from PlantUML class diagram (Stage 7)
  async generateCode(data) {
    try {
      console.log('Code generation request data:', data);
      const response = await apiClient.post('/generate-code', data);
      return response.data;
    } catch (error) {
      console.error('Code generation error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        requestData: data
      });
      throw new Error(`Code generation failed: ${error.message}`);
    }
  }
};
