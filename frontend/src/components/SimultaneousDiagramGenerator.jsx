import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Alert,
  CircularProgress,
  Chip,
  Divider,
  Paper
} from '@mui/material';
import {
  AutoAwesome as DiagramIcon,
  PlayArrow as GenerateIcon,
  CheckCircle as SuccessIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import PlantUMLViewer from './PlantUMLViewer';
import DiagramRetryControls from './DiagramRetryControls';
import { apiService } from '../services/apiService';

const SimultaneousDiagramGenerator = ({ 
  ruppSnlData, 
  originalRequirements,
  onDiagramsGenerated, 
  onError 
}) => {
  const [loading, setLoading] = useState(false);
  const [diagrams, setDiagrams] = useState(null);
  const [generationInfo, setGenerationInfo] = useState(null);
  const [retryLoading, setRetryLoading] = useState(false);

  const handleRetryComplete = (retryResult) => {
    console.log('Retry completed:', retryResult);
    
    const updatedDiagrams = {
      class_diagram: retryResult.classDiagram,
      sequence_diagram: retryResult.sequenceDiagram,
      generation_info: {
        method: 'GPT-3.5 (Retry)',
        retry_count: retryResult.retryCount,
        issue_type: retryResult.issueType,
        improvements: retryResult.improvements
      }
    };
    
    setDiagrams(updatedDiagrams);
    setGenerationInfo(updatedDiagrams.generation_info);
    
    // Notify parent component
    onDiagramsGenerated?.(updatedDiagrams);
  };

  const handleRetryError = (error) => {
    console.error('Retry error:', error);
    onError?.(error);
  };

  const handleGenerateDiagrams = async () => {
    if (!ruppSnlData?.snl_text) {
      onError('No RUPP SNL data available for diagram generation');
      return;
    }

    setLoading(true);
    try {
      console.log('Generating diagrams with RUPP SNL:', ruppSnlData.snl_text);
      
      const response = await apiService.generateBothDiagrams({
        rupp_snl_text: ruppSnlData.snl_text,
        snl_data: ruppSnlData // Keep for compatibility
      });

      const diagramsData = {
        class_diagram: response.class_diagram,
        sequence_diagram: response.sequence_diagram,
        generation_method: response.generation_method || 'gpt-3.5-turbo',
        timestamp: response.timestamp,
        original_requirements: originalRequirements
      };

      setDiagrams(diagramsData);
      setGenerationInfo({
        method: response.generation_method || 'GPT-3.5 Turbo',
        timestamp: new Date(response.timestamp).toLocaleString(),
        status: response.status
      });

      // Pass data to parent component
      if (onDiagramsGenerated) {
        onDiagramsGenerated(diagramsData);
      }

    } catch (error) {
      console.error('Diagram generation error:', error);
      onError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const getDiagramStats = (diagramCode) => {
    if (!diagramCode) return { lines: 0, elements: 0 };
    
    const lines = diagramCode.split('\n').length;
    const elements = (diagramCode.match(/class |actor |participant /g) || []).length;
    
    return { lines, elements };
  };

  return (
    <Box sx={{ p: 3 }}>
      <Card elevation={2} sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <DiagramIcon sx={{ mr: 2, color: 'primary.main' }} />
            <Typography variant="h5" component="h2">
              Screen 4: Simultaneous Diagram Generation
            </Typography>
          </Box>
          
          <Typography variant="body1" color="textSecondary" sx={{ mb: 3 }}>
            Generate both Class and Sequence diagrams simultaneously using RUPP SNL and GPT-3.5 Turbo.
            This creates the initial diagrams before actor identification and optimization.
          </Typography>

          {ruppSnlData && (
            <Alert severity="info" sx={{ mb: 3 }}>
              <Typography variant="body2">
                <strong>Ready to generate diagrams from RUPP SNL:</strong><br/>
                Text length: {ruppSnlData.snl_text?.length || 0} characters<br/>
                Processing time: {ruppSnlData.processing_time || 'N/A'} ms
              </Typography>
            </Alert>
          )}

          <Button
            variant="contained"
            size="large"
            startIcon={loading ? <CircularProgress size={16} /> : <GenerateIcon />}
            onClick={handleGenerateDiagrams}
            disabled={loading || !ruppSnlData?.snl_text}
            sx={{ mb: 2 }}
          >
            {loading ? 'Generating Diagrams...' : 'Generate Both Diagrams'}
          </Button>

          {generationInfo && (
            <Paper sx={{ p: 2, bgcolor: 'success.light', color: 'success.contrastText' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <SuccessIcon sx={{ mr: 1 }} />
                <Typography variant="h6">Generation Complete</Typography>
              </Box>
              <Typography variant="body2">
                Method: {generationInfo.method} | 
                Generated at: {generationInfo.timestamp} | 
                Status: {generationInfo.status}
              </Typography>
            </Paper>
          )}
        </CardContent>
      </Card>

      {diagrams && (
        <>
          {/* Retry Controls */}
          <DiagramRetryControls
            originalRequirements={originalRequirements}
            classDiagram={diagrams.class_diagram}
            sequenceDiagram={diagrams.sequence_diagram}
            identifiedActors={[]} // Will be populated when actors are identified
            onRetryComplete={handleRetryComplete}
            onError={handleRetryError}
            disabled={retryLoading}
          />

          <Grid container spacing={3}>
          {/* Class Diagram */}
          <Grid item xs={12} md={6}>
            <Card elevation={1}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6">Class Diagram</Typography>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Chip 
                      label={`${getDiagramStats(diagrams.class_diagram).elements} elements`} 
                      variant="outlined" 
                      size="small" 
                    />
                    <Chip 
                      label={`${getDiagramStats(diagrams.class_diagram).lines} lines`} 
                      variant="outlined" 
                      size="small" 
                    />
                  </Box>
                </Box>
                
                <PlantUMLViewer 
                  plantUMLCode={diagrams.class_diagram}
                  title="Initial Class Diagram"
                />
              </CardContent>
            </Card>
          </Grid>

          {/* Sequence Diagram */}
          <Grid item xs={12} md={6}>
            <Card elevation={1}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6">Sequence Diagram</Typography>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Chip 
                      label={`${getDiagramStats(diagrams.sequence_diagram).elements} elements`} 
                      variant="outlined" 
                      size="small" 
                    />
                    <Chip 
                      label={`${getDiagramStats(diagrams.sequence_diagram).lines} lines`} 
                      variant="outlined" 
                      size="small" 
                    />
                  </Box>
                </Box>
                
                <PlantUMLViewer 
                  plantUMLCode={diagrams.sequence_diagram}
                  title="Initial Sequence Diagram"
                />
              </CardContent>
            </Card>
          </Grid>

          {/* Generation Summary */}
          <Grid item xs={12}>
            <Card elevation={1}>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>Generation Summary</Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6} md={3}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="h4" color="primary">2</Typography>
                      <Typography variant="body2">Diagrams Generated</Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="h4" color="secondary">
                        {getDiagramStats(diagrams.class_diagram).elements + getDiagramStats(diagrams.sequence_diagram).elements}
                      </Typography>
                      <Typography variant="body2">Total Elements</Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="h4" color="info.main">
                        {generationInfo?.method || 'GPT-3.5'}
                      </Typography>
                      <Typography variant="body2">AI Model Used</Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={12} sm={6} md={3}>
                    <Paper sx={{ p: 2, textAlign: 'center' }}>
                      <Typography variant="h4" color="success.main">Ready</Typography>
                      <Typography variant="body2">Status</Typography>
                    </Paper>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
        </>
      )}

      {!diagrams && !loading && (
        <Card elevation={1}>
          <CardContent sx={{ textAlign: 'center', py: 8 }}>
            <InfoIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="textSecondary" gutterBottom>
              No Diagrams Generated Yet
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Click "Generate Both Diagrams" to create initial class and sequence diagrams using RUPP SNL.
            </Typography>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default SimultaneousDiagramGenerator;
