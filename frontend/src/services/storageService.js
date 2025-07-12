class StorageService {
  constructor() {
    this.CASE_STUDIES_KEY = 'nlp_case_studies';
    this.PREFERENCES_KEY = 'nlp_preferences';
    this.STATS_KEY = 'nlp_statistics';
  }

  // Case Studies Management
  saveCaseStudy(caseStudy) {
    try {
      const existing = this.getCaseStudies();
      const updated = [caseStudy, ...existing.slice(0, 49)]; // Keep last 50
      localStorage.setItem(this.CASE_STUDIES_KEY, JSON.stringify(updated));
      this.updateStatistics(caseStudy);
      return true;
    } catch (error) {
      console.error('Failed to save case study:', error);
      return false;
    }
  }

  getCaseStudies() {
    try {
      const data = localStorage.getItem(this.CASE_STUDIES_KEY);
      return data ? JSON.parse(data) : [];
    } catch (error) {
      console.error('Failed to load case studies:', error);
      return [];
    }
  }

  getCaseStudy(id) {
    const caseStudies = this.getCaseStudies();
    return caseStudies.find(cs => cs.id === id);
  }

  getRecentCaseStudies(limit = 5) {
    return this.getCaseStudies().slice(0, limit);
  }

  // Statistics Management
  updateStatistics(caseStudy) {
    try {
      const stats = this.getStatistics();
      
      stats.totalProcessed += 1;
      stats.lastProcessed = new Date().toISOString();
      
      // Add to processing history
      const historyEntry = {
        id: caseStudy.id,
        title: caseStudy.rupp_snl?.title || 'Untitled',
        timestamp: caseStudy.timestamp || new Date().toISOString(),
        metrics: caseStudy.comparison?.metrics || {}
      };
      
      stats.processingHistory = [historyEntry, ...stats.processingHistory.slice(0, 99)]; // Keep last 100
      
      // Update averages
      if (caseStudy.comparison?.metrics) {
        const metrics = caseStudy.comparison.metrics;
        stats.averageAccuracy = this.calculateRunningAverage(
          stats.averageAccuracy,
          metrics.accuracy || 0,
          stats.totalProcessed
        );
        stats.averagePrecision = this.calculateRunningAverage(
          stats.averagePrecision,
          metrics.precision || 0,
          stats.totalProcessed
        );
        stats.averageRecall = this.calculateRunningAverage(
          stats.averageRecall,
          metrics.recall || 0,
          stats.totalProcessed
        );
      }
      
      localStorage.setItem(this.STATS_KEY, JSON.stringify(stats));
    } catch (error) {
      console.error('Failed to update statistics:', error);
    }
  }

  getStatistics() {
    try {
      const data = localStorage.getItem(this.STATS_KEY);
      return data ? JSON.parse(data) : {
        totalProcessed: 0,
        averageAccuracy: 0,
        averagePrecision: 0,
        averageRecall: 0,
        lastProcessed: null,
        processingHistory: []
      };
    } catch (error) {
      console.error('Failed to load statistics:', error);
      return {
        totalProcessed: 0,
        averageAccuracy: 0,
        averagePrecision: 0,
        averageRecall: 0,
        lastProcessed: null,
        processingHistory: []
      };
    }
  }

  calculateRunningAverage(currentAvg, newValue, count) {
    if (count === 1) return newValue;
    return (currentAvg * (count - 1) + newValue) / count;
  }

  // Preferences Management
  savePreferences(preferences) {
    try {
      localStorage.setItem(this.PREFERENCES_KEY, JSON.stringify(preferences));
      return true;
    } catch (error) {
      console.error('Failed to save preferences:', error);
      return false;
    }
  }

  getPreferences() {
    try {
      const data = localStorage.getItem(this.PREFERENCES_KEY);
      return data ? JSON.parse(data) : {
        theme: 'light',
        autoSave: true,
        notifications: true,
        defaultDiagramType: 'class',
        exportFormat: 'json'
      };
    } catch (error) {
      console.error('Failed to load preferences:', error);
      return {
        theme: 'light',
        autoSave: true,
        notifications: true,
        defaultDiagramType: 'class',
        exportFormat: 'json'
      };
    }
  }

  // Data Export/Import
  exportData() {
    try {
      const data = {
        caseStudies: this.getCaseStudies(),
        statistics: this.getStatistics(),
        preferences: this.getPreferences(),
        exportDate: new Date().toISOString(),
        version: '1.0.0'
      };
      
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      
      const a = document.createElement('a');
      a.href = url;
      a.download = `nlp-research-data-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      return true;
    } catch (error) {
      console.error('Failed to export data:', error);
      return false;
    }
  }

  importData(jsonData) {
    try {
      const data = typeof jsonData === 'string' ? JSON.parse(jsonData) : jsonData;
      
      if (data.caseStudies) {
        localStorage.setItem(this.CASE_STUDIES_KEY, JSON.stringify(data.caseStudies));
      }
      
      if (data.statistics) {
        localStorage.setItem(this.STATS_KEY, JSON.stringify(data.statistics));
      }
      
      if (data.preferences) {
        localStorage.setItem(this.PREFERENCES_KEY, JSON.stringify(data.preferences));
      }
      
      return true;
    } catch (error) {
      console.error('Failed to import data:', error);
      return false;
    }
  }

  // Clear all data
  clearAllData() {
    try {
      localStorage.removeItem(this.CASE_STUDIES_KEY);
      localStorage.removeItem(this.STATS_KEY);
      // Keep preferences
      return true;
    } catch (error) {
      console.error('Failed to clear data:', error);
      return false;
    }
  }

  // Search functionality
  searchCaseStudies(query, limit = 10) {
    try {
      const caseStudies = this.getCaseStudies();
      const queryLower = query.toLowerCase();
      
      return caseStudies
        .filter(cs => {
          const title = (cs.rupp_snl?.title || '').toLowerCase();
          const originalText = (cs.original_text || '').toLowerCase();
          return title.includes(queryLower) || originalText.includes(queryLower);
        })
        .slice(0, limit);
    } catch (error) {
      console.error('Failed to search case studies:', error);
      return [];
    }
  }

  // Load from storage on startup
  loadFromStorage() {
    try {
      // Pre-load data to ensure everything is accessible
      this.getCaseStudies();
      this.getStatistics();
      this.getPreferences();
      
      // Return current session data if available
      return this.getCurrentSession();
    } catch (error) {
      console.error('Failed to load from storage:', error);
      return null;
    }
  }

  // Get storage usage information
  getStorageInfo() {
    try {
      let totalSize = 0;
      let itemCount = 0;
      
      for (let key in localStorage) {
        if (localStorage.hasOwnProperty(key) && key.startsWith('nlp_')) {
          totalSize += localStorage[key].length;
          itemCount++;
        }
      }
      
      return {
        totalSize: `${(totalSize / 1024).toFixed(2)} KB`,
        itemCount,
        caseStudiesCount: this.getCaseStudies().length,
        lastUpdate: this.getStatistics().lastProcessed
      };
    } catch (error) {
      console.error('Failed to get storage info:', error);
      return {
        totalSize: '0 KB',
        itemCount: 0,
        caseStudiesCount: 0,
        lastUpdate: null
      };
    }
  }

  // Session State Management
  saveCurrentSession(sessionData) {
    try {
      localStorage.setItem('nlp_current_session', JSON.stringify({
        ...sessionData,
        timestamp: new Date().toISOString()
      }));
      return true;
    } catch (error) {
      console.error('Failed to save current session:', error);
      return false;
    }
  }

  getCurrentSession() {
    try {
      const data = localStorage.getItem('nlp_current_session');
      return data ? JSON.parse(data) : null;
    } catch (error) {
      console.error('Failed to load current session:', error);
      return null;
    }
  }

  clearCurrentSession() {
    try {
      localStorage.removeItem('nlp_current_session');
      return true;
    } catch (error) {
      console.error('Failed to clear current session:', error);
      return false;
    }
  }
}

export const storageService = new StorageService();
