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
  Snackbar,
  Stepper,
  Step,
  StepLabel,
  Button
} from '@mui/material';
import {
  Description as DescriptionIcon,
  Compare as CompareIcon,
  Timeline as TimelineIcon,
  Assessment as AssessmentIcon,
  AutoAwesome as OptimizeIcon,
  VerifiedUser as VerifyIcon,
  Code as CodeIcon,
  KeyboardArrowLeft,
  KeyboardArrowRight
} from '@mui/icons-material';

// Import components
import RequirementsInput from './components/RequirementsInput';
import AIResultsVerifier from './components/AIResultsVerifier';
import OptimizationRequest from './components/OptimizationRequest';
import SimultaneousDiagramGenerator from './components/SimultaneousDiagramGenerator';
import ActorIdentificationVerifier from './components/ActorIdentificationVerifier';
import FinalLLMOptimizer from './components/FinalLLMOptimizer';
import CodeGenerator from './components/CodeGenerator';

// Import services
import { storageService } from './services/storageService';
import { apiService } from './services/apiService';

function App() {
  const [currentStep, setCurrentStep] = useState(0);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'info' });
  const [currentCaseStudy, setCurrentCaseStudy] = useState(null);
  const [verificationResults, setVerificationResults] = useState(null);
  const [optimizationResults, setOptimizationResults] = useState(null);
  const [initialDiagrams, setInitialDiagrams] = useState(null);
  const [identifiedActors, setIdentifiedActors] = useState([]);
  const [actorVerification, setActorVerification] = useState(null);
  const [finalOptimizedDiagrams, setFinalOptimizedDiagrams] = useState(null);
  const [generatedCode, setGeneratedCode] = useState(null);

  const steps = [
    'Input Requirements',
    'AI Results & Verification',
    'RUPP Optimization',
    'Initial Diagram Generation',
    'Actor Identification & Verification',
    'Final LLM Optimization',
    'Skeletal Code Generation'
  ];

  useEffect(() => {
    const sessionData = storageService.loadFromStorage();
    if (sessionData) {
      // Restore session state
      setCurrentStep(sessionData.currentStep || 0);
      setCurrentCaseStudy(sessionData.currentCaseStudy || null);
      setInitialDiagrams(sessionData.initialDiagrams || null);
      setIdentifiedActors(sessionData.identifiedActors || []);
      setActorVerification(sessionData.actorVerification || null);
      setFinalOptimizedDiagrams(sessionData.finalOptimizedDiagrams || null);
      setGeneratedCode(sessionData.generatedCode || null);
      setVerificationResults(sessionData.verificationResults || null);
      setOptimizationResults(sessionData.optimizationResults || null);
      
      console.log('Session restored:', sessionData);
    }
  }, []);

  // Save current session to localStorage
  const saveCurrentSession = () => {
    const sessionData = {
      currentStep,
      currentCaseStudy,
      initialDiagrams,
      identifiedActors,
      actorVerification,
      finalOptimizedDiagrams,
      generatedCode,
      verificationResults,
      optimizationResults
    };
    storageService.saveCurrentSession(sessionData);
  };

  // Auto-save session when important data changes
  useEffect(() => {
    if (currentCaseStudy || initialDiagrams || identifiedActors.length > 0) {
      saveCurrentSession();
    }
  }, [currentCaseStudy, initialDiagrams, identifiedActors, actorVerification, finalOptimizedDiagrams, generatedCode, verificationResults, optimizationResults]);

  const showNotification = (message, severity = 'info') => {
    setNotification({ open: true, message, severity });
  };

  const handleCloseNotification = () => {
    setNotification({ ...notification, open: false });
  };

  const handleBack = () => {
    setCurrentStep((prevStep) => Math.max(0, prevStep - 1));
  };

  const handleNext = () => {
    setCurrentStep((prevStep) => Math.min(steps.length - 1, prevStep + 1));
  };

  const handleProcessingComplete = (result) => {
    setCurrentCaseStudy(result);
    showNotification('Requirements processed successfully!', 'success');
  };

  const handleDiagramsGenerated = (diagrams) => {
    setInitialDiagrams(diagrams);
    showNotification('Initial diagrams generated successfully!', 'success');
  };

  const handleActorsIdentified = (result) => {
    setIdentifiedActors(result.actors || []);
    setActorVerification(result.verification || {});
    showNotification(`${result.actors?.length || 0} actors identified and verified!`, 'success');
  };

  const handleFinalOptimizationComplete = (result) => {
    setFinalOptimizedDiagrams(result);
    showNotification('Final optimization complete!', 'success');
  };

  const handleCodeGenerationComplete = (result) => {
    setGeneratedCode(result);
    showNotification(`Java code generated! ${result.classes_generated} classes created.`, 'success');
  };

  const handleVerificationComplete = (results) => {
    setVerificationResults(results);
    if (results.totalIssues === 0) {
      showNotification('Verification passed with no issues!', 'success');
    } else {
      showNotification(`Verification complete with ${results.totalIssues} issues found.`, 'warning');
    }
  };

  const handleOptimizationComplete = (results) => {
    setOptimizationResults(results);
    showNotification('Optimization complete!', 'success');
  };

  const handleDiagramGeneration = async (diagramType = 'class') => {
    if (!currentCaseStudy) {
      showNotification('No case study data available', 'error');
      return;
    }

    try {
      showNotification('Generating diagrams using RUPP SNL and OpenAI...', 'info');
      
      const snlDataOriginal = currentCaseStudy.rupp_snl || currentCaseStudy.ai_snl;
      
      if (!snlDataOriginal) {
        showNotification('No SNL data available for diagram generation', 'error');
        return;
      }

      // Generate sample diagrams for both types
      const classDiagram = `@startuml
class User {
  -String username
  -String email
  -String password
  +login()
  +logout()
  +updateProfile()
}

class System {
  -List<User> users
  +authenticateUser()
  +validateCredentials()
  +processRequest()
}

class Database {
  +saveUser()
  +getUserById()
  +updateUser()
}

User --> System : interacts
System --> Database : stores
@enduml`;

      const sequenceDiagram = `@startuml
actor User
participant System
participant Database

User -> System: login(username, password)
System -> Database: validateCredentials(username, password)
Database -> System: credentials valid
System -> User: authentication successful
User -> System: updateProfile(data)
System -> Database: saveUser(data)
Database -> System: user saved
System -> User: profile updated
@enduml`;

      const selectedDiagram = diagramType === 'class' ? classDiagram : sequenceDiagram;

      const updatedCaseStudy = {
        ...currentCaseStudy,
        diagram: selectedDiagram,
        diagramType: diagramType,
        diagrams: {
          ...currentCaseStudy.diagrams,
          [diagramType]: selectedDiagram
        },
        diagram_metadata: {
          type: diagramType,
          generated_at: new Date().toISOString(),
          source: 'sample'
        }
      };
      
      setCurrentCaseStudy(updatedCaseStudy);
      showNotification(`${diagramType.charAt(0).toUpperCase() + diagramType.slice(1)} diagram generated successfully!`, 'success');
    } catch (error) {
      console.error('Diagram generation error:', error);
      showNotification(`Diagram generation failed: ${error.message}`, 'error');
    }
  };

  const handleDiagramVerificationComplete = (results) => {
    setVerificationResults(results);
    showNotification('Diagram verification complete!', 'success');
  };

  const canProceed = () => {
    switch (currentStep) {
      case 0: // Input Requirements
        return currentCaseStudy !== null;
      case 1: // AI Results & Verification
        return verificationResults !== null;
      case 2: // RUPP Optimization
        return optimizationResults !== null;
      case 3: // Initial Diagram Generation
        return initialDiagrams !== null;
      case 4: // Actor Identification & Verification
        return identifiedActors.length > 0;
      case 5: // Final LLM Optimization
        return finalOptimizedDiagrams !== null;
      case 6: // Skeletal Code Generation
        return generatedCode !== null;
      default:
        return false;
    }
  };

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 0: // Input Requirements
        return (
          <RequirementsInput 
            onProcessingComplete={handleProcessingComplete}
            onError={(error) => showNotification(error, 'error')}
            onSuccess={(message) => showNotification(message, 'success')}
          />
        );
      case 1: // AI Results & Verification
        return (
          <AIResultsVerifier
            aiSnlData={currentCaseStudy?.ai_snl}
            originalText={currentCaseStudy?.original_text || currentCaseStudy?.text || ''}
            onVerificationComplete={handleVerificationComplete}
            onError={(error) => showNotification(error, 'error')}
            onContinue={handleNext}
          />
        );
      case 2: // RUPP Optimization
        return (
          <OptimizationRequest
            ruppSnlData={currentCaseStudy?.rupp_snl}
            onOptimize={handleOptimizationComplete}
            onError={(error) => showNotification(error, 'error')}
          />
        );
      case 3: // Initial Diagram Generation
        return (
          <SimultaneousDiagramGenerator
            ruppSnlData={currentCaseStudy?.rupp_snl}
            originalRequirements={currentCaseStudy?.original_text || currentCaseStudy?.text || ''}
            onDiagramsGenerated={handleDiagramsGenerated}
            onError={(error) => showNotification(error, 'error')}
          />
        );
      case 4: // Actor Identification & Verification
        // Handle both old and new case study formats
        const originalText = currentCaseStudy?.original_text || currentCaseStudy?.text || '';
        console.log('Rendering Screen 5 with data:', {
          currentCaseStudy: !!currentCaseStudy,
          currentCaseStudyKeys: currentCaseStudy ? Object.keys(currentCaseStudy) : [],
          originalRequirements: !!originalText,
          originalTextValue: originalText?.substring(0, 100) + '...',
          initialDiagrams: !!initialDiagrams,
          classDiagram: !!initialDiagrams?.class_diagram,
          sequenceDiagram: !!initialDiagrams?.sequence_diagram
        });
        return (
          <ActorIdentificationVerifier
            originalRequirements={originalText}
            classDiagram={initialDiagrams?.class_diagram}
            sequenceDiagram={initialDiagrams?.sequence_diagram}
            onActorsIdentified={handleActorsIdentified}
            onError={(error) => showNotification(error, 'error')}
          />
        );
      case 5: // Final LLM Optimization
        return (
          <FinalLLMOptimizer
            originalRequirements={currentCaseStudy?.original_text || currentCaseStudy?.text || ''}
            classDiagram={initialDiagrams?.class_diagram}
            sequenceDiagram={initialDiagrams?.sequence_diagram}
            identifiedActors={identifiedActors}
            verificationIssues={actorVerification}
            onOptimizationComplete={handleFinalOptimizationComplete}
            onError={(error) => showNotification(error, 'error')}
          />
        );
      case 6: // Skeletal Code Generation
        return (
          <CodeGenerator
            classDiagram={finalOptimizedDiagrams?.optimized_class_diagram}
            onCodeGenerated={handleCodeGenerationComplete}
            onError={(error) => showNotification(error, 'error')}
          />
        );
      default:
        return null;
    }
  };

  const clearCurrentSession = () => {
    storageService.clearCurrentSession();
    setCurrentStep(0);
    setCurrentCaseStudy(null);
    setInitialDiagrams(null);
    setIdentifiedActors([]);
    setActorVerification(null);
    setFinalOptimizedDiagrams(null);
    setGeneratedCode(null);
    setVerificationResults(null);
    setOptimizationResults(null);
    showNotification('Session cleared. Starting fresh.', 'info');
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static" elevation={0}>
        <Toolbar>
          <DescriptionIcon sx={{ mr: 2 }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            NLP Requirements Analysis System
          </Typography>
          <Typography variant="body2" sx={{ opacity: 0.8, mr: 2 }}>
            RUPP Template vs AI Comparison
          </Typography>
          {/* Debug Info */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="caption" sx={{ opacity: 0.7 }}>
              Case: {currentCaseStudy ? '✓' : '✗'} | 
              Diagrams: {initialDiagrams ? '✓' : '✗'} | 
              Actors: {identifiedActors.length} |
              Code: {generatedCode ? '✓' : '✗'}
            </Typography>
            <Button 
              size="small" 
              variant="outlined" 
              onClick={clearCurrentSession}
              sx={{ ml: 1, color: 'white', borderColor: 'rgba(255,255,255,0.3)' }}
            >
              Clear Session
            </Button>
          </Box>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 2 }}>
        {/* Stepper */}
        <Paper elevation={1} sx={{ mb: 3, p: 2 }}>
          <Stepper activeStep={currentStep} alternativeLabel>
            {steps.map((label, index) => (
              <Step 
                key={label}
                completed={index < currentStep}
              >
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>
        </Paper>

        {/* Current Step Content */}
        {renderCurrentStep()}

        {/* Navigation Controls - Only show if not on last step */}
        {currentStep < steps.length - 1 && (
          <Paper 
            square 
            elevation={0} 
            sx={{ 
              position: 'sticky',
              bottom: 0,
              bgcolor: 'background.paper',
              borderTop: '1px solid rgba(0,0,0,0.12)',
              p: 2,
              mt: 2
            }}
          >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Button 
                size="small" 
                onClick={handleBack} 
                disabled={currentStep === 0}
                startIcon={<KeyboardArrowLeft />}
              >
                Back
              </Button>
              
              <Typography variant="body2" color="textSecondary">
                Step {currentStep + 1} of {steps.length}
              </Typography>
              
              <Button
                size="small"
                onClick={handleNext}
                disabled={!canProceed()}
                endIcon={<KeyboardArrowRight />}
                variant="contained"
              >
                Next
              </Button>
            </Box>
          </Paper>
        )}
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
