import React, { useState, useEffect } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  Tabs,
  Tab,
  Paper,
  Alert,
  Snackbar
} from '@mui/material';
import {
  Description as DescriptionIcon,
  Compare as CompareIcon,
  Timeline as TimelineIcon,
  Assessment as AssessmentIcon
} from '@mui/icons-material';

// Import components
import RequirementsInput from './components/RequirementsInput';
import SNLComparison from './components/SNLComparison';
import DiagramViewer from './components/DiagramViewer';
import StatsDashboard from './components/StatsDashboard';

// Import services
import { storageService } from './services/storageService';
import { apiService } from './services/apiService';

function App() {
  const [currentTab, setCurrentTab] = useState(0);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'info' });
  const [currentCaseStudy, setCurrentCaseStudy] = useState(null);

  useEffect(() => {
    // Load any existing data from localStorage on startup
    storageService.loadFromStorage();
  }, []);

  const handleTabChange = (event, newValue) => {
    setCurrentTab(newValue);
  };

  const showNotification = (message, severity = 'info') => {
    setNotification({ open: true, message, severity });
  };

  const handleCloseNotification = () => {
    setNotification({ ...notification, open: false });
  };

  const handleProcessingComplete = (result) => {
    setCurrentCaseStudy(result);
    showNotification('Requirements processed successfully!', 'success');
    setCurrentTab(1); // Switch to comparison tab
  };
  const handleDiagramGeneration = async (diagramType = 'class') => {
    if (!currentCaseStudy) {
      showNotification('No case study data available', 'error');
      return;
    }

    try {
      showNotification('Generating diagrams using RUPP SNL and OpenAI...', 'info');
      
      // Use RUPP SNL data for diagram generation (as requested)
      const snlData = currentCaseStudy.rupp_snl || currentCaseStudy.ai_snl;
      
      if (!snlData) {
        showNotification('No SNL data available for diagram generation', 'error');
        return;
      }

      const response = await apiService.generateDiagrams({
        snl_data: snlData,
        diagram_type: diagramType
      });

      // Update current case study with diagram data
      const updatedCaseStudy = {
        ...currentCaseStudy,
        diagram: response.diagram_code,
        diagramType: diagramType
      };
      
      setCurrentCaseStudy(updatedCaseStudy);
      showNotification(`${diagramType.charAt(0).toUpperCase() + diagramType.slice(1)} diagram generated successfully using RUPP SNL!`, 'success');
      
    } catch (error) {
      showNotification(`Diagram generation failed: ${error.message}`, 'error');
    }
  };

  const TabPanel = ({ children, value, index, ...other }) => (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static" elevation={0}>
        <Toolbar>
          <DescriptionIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            NLP Requirements Analysis System
          </Typography>
          <Typography variant="body2" sx={{ opacity: 0.8 }}>
            RUPP Template vs AI Comparison
          </Typography>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 2 }}>
        <Paper elevation={1} sx={{ mb: 2 }}>
          <Tabs
            value={currentTab}
            onChange={handleTabChange}
            aria-label="requirements analysis tabs"
            variant="fullWidth"
          >
            <Tab
              icon={<DescriptionIcon />}
              label="Input Requirements"
              id="tab-0"
              aria-controls="tabpanel-0"
            />
            <Tab
              icon={<CompareIcon />}
              label="SNL Comparison"
              id="tab-1"
              aria-controls="tabpanel-1"
              disabled={!currentCaseStudy}
            />
            <Tab
              icon={<TimelineIcon />}
              label="UML Diagrams"
              id="tab-2"
              aria-controls="tabpanel-2"
              disabled={!currentCaseStudy}
            />
            <Tab
              icon={<AssessmentIcon />}
              label="Statistics"
              id="tab-3"
              aria-controls="tabpanel-3"
            />
          </Tabs>
        </Paper>

        <TabPanel value={currentTab} index={0}>
          <RequirementsInput 
            onProcessingComplete={handleProcessingComplete}
            onError={(error) => showNotification(error, 'error')}
          />
        </TabPanel>

        <TabPanel value={currentTab} index={1}>
          {currentCaseStudy ? (
            <SNLComparison 
              caseStudyData={currentCaseStudy}
              onError={(error) => showNotification(error, 'error')}
            />
          ) : (
            <Alert severity="info">
              Please process a case study first to view the comparison.
            </Alert>
          )}
        </TabPanel>        <TabPanel value={currentTab} index={2}>
          {currentCaseStudy ? (
            <DiagramViewer 
              diagramData={currentCaseStudy.diagram}
              caseStudyData={currentCaseStudy}
              onGenerateDiagram={handleDiagramGeneration}
            />
          ) : (
            <Alert severity="info">
              Please process a case study first to view the diagrams.
            </Alert>
          )}
        </TabPanel>

        <TabPanel value={currentTab} index={3}>
          <StatsDashboard 
            comparisonResults={currentCaseStudy?.comparison}
          />
        </TabPanel>
      </Container>

      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={handleCloseNotification}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={handleCloseNotification}
          severity={notification.severity}
          sx={{ width: '100%' }}
        >
          {notification.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}

export default App;
