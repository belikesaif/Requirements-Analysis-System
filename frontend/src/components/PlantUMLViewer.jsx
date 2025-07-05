import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  Tabs,
  Tab,
  CircularProgress,
  Alert,
  Switch,
  FormControlLabel,
  Button,
  Chip
} from '@mui/material';
import { 
  Refresh as RefreshIcon,
  ErrorOutline as ErrorIcon,
  Warning as WarningIcon
} from '@mui/icons-material';
import { encode } from 'plantuml-encoder';
import { apiService } from '../services/apiService';

const PlantUMLViewer = ({ 
  plantUMLCode, 
  title = "UML Diagram", 
  showCodeToggle = true,
  onError = null,
  diagramType = "unknown"
}) => {
  const [activeTab, setActiveTab] = useState(0);
  const [showCode, setShowCode] = useState(false);
  const [imageUrl, setImageUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [retryCount, setRetryCount] = useState(0);
  const [validationStatus, setValidationStatus] = useState(null);
  const [imageLoadAttempts, setImageLoadAttempts] = useState(0);

  const MAX_RETRY_ATTEMPTS = 3;
  const IMAGE_LOAD_TIMEOUT = 15000; // 15 seconds

  // Report error to backend for analysis
  const reportErrorToBackend = useCallback(async (errorDetails) => {
    try {
      await apiService.reportPlantUMLError({
        diagram_type: diagramType,
        error_type: errorDetails.type,
        error_message: errorDetails.message,
        plantuml_code: plantUMLCode,
        retry_count: retryCount,
        timestamp: new Date().toISOString(),
        validation_status: validationStatus
      });
    } catch (err) {
      console.error('Failed to report error to backend:', err);
    }
  }, [diagramType, plantUMLCode, retryCount, validationStatus]);

  // Validate PlantUML syntax before rendering
  const validatePlantUMLSyntax = useCallback(async () => {
    if (!plantUMLCode) return false;
    
    try {
      const result = await apiService.validatePlantUMLSyntax({
        plantuml_code: plantUMLCode,
        diagram_type: diagramType
      });
      setValidationStatus(result);
      return result.is_valid;
    } catch (err) {
      console.error('PlantUML validation failed:', err);
      setValidationStatus({ is_valid: false, errors: [err.message] });
      return false;
    }
  }, [plantUMLCode, diagramType]);

  useEffect(() => {
    if (plantUMLCode && activeTab === 0) {
      generateDiagramUrl();
    }
  }, [plantUMLCode, activeTab]);

  const generateDiagramUrl = async () => {
    if (!plantUMLCode) return;
    
    setIsLoading(true);
    setError('');
    
    try {
      // First validate the syntax if this is a retry or first attempt
      if (retryCount === 0) {
        const isValid = await validatePlantUMLSyntax();
        if (!isValid && validationStatus?.errors?.length > 0) {
          const validationError = `PlantUML syntax errors: ${validationStatus.errors.join(', ')}`;
          setError(validationError);
          await reportErrorToBackend({
            type: 'syntax_validation',
            message: validationError
          });
          if (onError) onError(validationError);
          return;
        }
      }

      // Clean the PlantUML code
      const cleanCode = plantUMLCode.trim();
      
      // Encode the PlantUML code
      const encoded = encode(cleanCode);
      
      // Use the PlantUML server to generate the diagram
      const url = `https://www.plantuml.com/plantuml/svg/${encoded}`;
      setImageUrl(url);
      setImageLoadAttempts(0);
      
    } catch (err) {
      console.error('Error generating diagram:', err);
      const errorMessage = 'Failed to generate diagram. Please check the PlantUML syntax.';
      setError(errorMessage);
      
      await reportErrorToBackend({
        type: 'generation_error',
        message: err.message
      });
      
      if (onError) onError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle image load errors with retry logic
  const handleImageError = useCallback(async () => {
    const newAttempts = imageLoadAttempts + 1;
    setImageLoadAttempts(newAttempts);
    
    if (newAttempts < MAX_RETRY_ATTEMPTS) {
      // Try alternative PlantUML servers
      const servers = [
        'https://www.plantuml.com/plantuml/svg',
        'https://plantuml-server.kkeisuke.dev/svg',
        'http://www.plantuml.com/plantuml/png' // Fallback to PNG
      ];
      
      const encoded = encode(plantUMLCode.trim());
      const alternativeUrl = `${servers[newAttempts]}/${encoded}`;
      setImageUrl(alternativeUrl);
      
      console.log(`Retrying with alternative server (attempt ${newAttempts}): ${servers[newAttempts]}`);
      
    } else {
      const errorMessage = `Failed to load diagram image after ${MAX_RETRY_ATTEMPTS} attempts`;
      setError(errorMessage);
      
      await reportErrorToBackend({
        type: 'image_load_error',
        message: errorMessage
      });
      
      if (onError) onError(errorMessage);
    }
  }, [imageLoadAttempts, plantUMLCode, onError, reportErrorToBackend]);

  // Retry generation
  const handleRetry = useCallback(() => {
    if (retryCount < MAX_RETRY_ATTEMPTS) {
      setRetryCount(prev => prev + 1);
      setError('');
      setImageUrl('');
      setImageLoadAttempts(0);
      generateDiagramUrl();
    }
  }, [retryCount, generateDiagramUrl]);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  if (!plantUMLCode) {
    return (
      <Alert severity="info">
        No PlantUML code available to display.
      </Alert>
    );
  }

  return (
    <Paper elevation={2} sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="h6">{title}</Typography>
          {validationStatus && (
            <Chip
              size="small"
              icon={validationStatus.is_valid ? <WarningIcon /> : <ErrorIcon />}
              label={validationStatus.is_valid ? "Valid" : "Syntax Issues"}
              color={validationStatus.is_valid ? "success" : "error"}
              variant="outlined"
            />
          )}
          {retryCount > 0 && (
            <Chip
              size="small"
              label={`Retry ${retryCount}/${MAX_RETRY_ATTEMPTS}`}
              color="warning"
              variant="outlined"
            />
          )}
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {error && retryCount < MAX_RETRY_ATTEMPTS && (
            <Button
              size="small"
              startIcon={<RefreshIcon />}
              onClick={handleRetry}
              variant="outlined"
              color="primary"
            >
              Retry
            </Button>
          )}
          {showCodeToggle && (
            <FormControlLabel
              control={
                <Switch
                  checked={showCode}
                  onChange={(e) => setShowCode(e.target.checked)}
                  size="small"
                />
              }
              label="Show Code"
              labelPlacement="start"
            />
          )}
        </Box>
      </Box>

      <Tabs value={showCode ? 1 : 0} onChange={(e, val) => setShowCode(val === 1)} sx={{ mb: 2 }}>
        <Tab label="Diagram View" />
        <Tab label="Code View" />
      </Tabs>

      {showCode ? (
        // Code View
        <Box
          sx={{
            bgcolor: 'grey.50',
            p: 2,
            borderRadius: 1,
            border: '1px solid rgba(0,0,0,0.12)',
            minHeight: '300px',
            maxHeight: '600px',
            overflow: 'auto'
          }}
        >
          <pre style={{ 
            margin: 0, 
            fontFamily: 'monospace',
            fontSize: '12px',
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word'
          }}>
            {plantUMLCode}
          </pre>
        </Box>
      ) : (
        // Diagram View
        <Box
          sx={{
            minHeight: '400px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: '1px solid rgba(0,0,0,0.12)',
            borderRadius: 1,
            bgcolor: 'background.paper',
            position: 'relative'
          }}
        >
          {isLoading ? (
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <CircularProgress size={40} sx={{ mb: 2 }} />
              <Typography variant="body2" color="textSecondary">
                Generating diagram...
              </Typography>
            </Box>
          ) : error ? (
            <Box sx={{ width: '100%', textAlign: 'center' }}>
              <Alert 
                severity="error" 
                sx={{ mb: 2 }}
                action={
                  retryCount < MAX_RETRY_ATTEMPTS && (
                    <Button
                      color="inherit"
                      size="small"
                      startIcon={<RefreshIcon />}
                      onClick={handleRetry}
                    >
                      Retry
                    </Button>
                  )
                }
              >
                <Typography variant="body2" sx={{ mb: 1 }}>
                  {error}
                </Typography>
                {validationStatus && !validationStatus.is_valid && (
                  <Typography variant="caption" color="textSecondary">
                    Validation errors: {validationStatus.errors?.join(', ')}
                  </Typography>
                )}
                {retryCount >= MAX_RETRY_ATTEMPTS && (
                  <Typography variant="caption" color="textSecondary" sx={{ display: 'block', mt: 1 }}>
                    Max retry attempts reached. Please check the PlantUML code or contact support.
                  </Typography>
                )}
              </Alert>
              
              {/* Show fallback text representation when image fails */}
              <Box sx={{ 
                bgcolor: 'grey.50', 
                p: 2, 
                border: '1px dashed grey.300',
                borderRadius: 1,
                textAlign: 'left'
              }}>
                <Typography variant="subtitle2" gutterBottom>
                  Fallback: PlantUML Code Preview
                </Typography>
                <pre style={{ 
                  margin: 0, 
                  fontFamily: 'monospace',
                  fontSize: '11px',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                  maxHeight: '300px',
                  overflow: 'auto'
                }}>
                  {plantUMLCode}
                </pre>
              </Box>
            </Box>
          ) : imageUrl ? (
            <img
              src={imageUrl}
              alt="PlantUML Diagram"
              style={{
                maxWidth: '100%',
                maxHeight: '600px',
                objectFit: 'contain'
              }}
              onError={handleImageError}
              onLoad={() => {
                // Reset error states on successful load
                setError('');
                setImageLoadAttempts(0);
              }}
            />
          ) : (
            <Typography variant="body2" color="textSecondary">
              Click on Diagram View to generate the visual diagram
            </Typography>
          )}
        </Box>
      )}
    </Paper>
  );
};

export default PlantUMLViewer;
