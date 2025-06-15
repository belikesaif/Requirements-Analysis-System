import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  CircularProgress,
  Alert,
  ButtonGroup,
  Divider,
  Tabs,
  Tab
} from '@mui/material';
import { 
  Download as DownloadIcon,
  AccountTree as ClassIcon,
  Timeline as SequenceIcon,
  Visibility as ViewIcon,
  Code as CodeIcon
} from '@mui/icons-material';
import plantumlEncoder from 'plantuml-encoder';

const DiagramViewer = ({ diagramData, caseStudyData, onGenerateDiagram }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [diagramType, setDiagramType] = useState('class');
  const [viewMode, setViewMode] = useState(0); // 0 = diagram view, 1 = code view

  const handleGenerateDiagram = async (type = diagramType) => {
    setLoading(true);
    setError(null);
    try {
      await onGenerateDiagram(type);
      setDiagramType(type);
    } catch (err) {
      setError(`Failed to generate ${type} diagram: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!diagramData) return;
    
    const blob = new Blob([diagramData], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${diagramType}-diagram.puml`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const getPlantUMLImageUrl = () => {
    if (!diagramData) return null;
    
    try {
      const encoded = plantumlEncoder.encode(diagramData);
      return `http://www.plantuml.com/plantuml/png/${encoded}`;
    } catch (error) {
      console.error('Error encoding PlantUML:', error);
      return null;
    }
  };

  const handleTabChange = (event, newValue) => {
    setViewMode(newValue);
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        UML Diagrams
      </Typography>
      
      <Paper elevation={3} sx={{ p: 3, mt: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">
            Generate System Diagrams
          </Typography>
          
          <ButtonGroup variant="outlined">
            <Button
              startIcon={<ClassIcon />}
              onClick={() => handleGenerateDiagram('class')}
              disabled={loading}
              variant={diagramType === 'class' ? 'contained' : 'outlined'}
            >
              Class Diagram
            </Button>
            <Button
              startIcon={<SequenceIcon />}
              onClick={() => handleGenerateDiagram('sequence')}
              disabled={loading}
              variant={diagramType === 'sequence' ? 'contained' : 'outlined'}
            >
              Sequence Diagram
            </Button>
          </ButtonGroup>
        </Box>

        <Divider sx={{ mb: 2 }} />        {!caseStudyData && (
          <Alert severity="info" sx={{ mb: 2 }}>
            Please process a case study first to generate diagrams.
          </Alert>
        )}

        {caseStudyData && (
          <Alert severity="info" sx={{ mb: 2 }}>
            Diagrams are generated from <strong>RUPP Template SNL</strong> using OpenAI ChatGPT for intelligent UML creation.
          </Alert>
        )}

        {loading && (
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <CircularProgress size={20} sx={{ mr: 1 }} />
            <Typography variant="body2">Generating {diagramType} diagram...</Typography>
          </Box>
        )}

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}        {diagramData && !loading && (
          <Box>
            <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
              <Tabs value={viewMode} onChange={handleTabChange}>
                <Tab 
                  icon={<ViewIcon />} 
                  label="Diagram View" 
                  id="diagram-tab-0"
                  aria-controls="diagram-tabpanel-0"
                />
                <Tab 
                  icon={<CodeIcon />} 
                  label="PlantUML Code" 
                  id="diagram-tab-1"
                  aria-controls="diagram-tabpanel-1"
                />
              </Tabs>
            </Box>

            {/* Diagram View */}
            {viewMode === 0 && (
              <Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="subtitle1">
                    {diagramType.charAt(0).toUpperCase() + diagramType.slice(1)} Diagram Visualization
                  </Typography>
                  <Button
                    variant="outlined"
                    startIcon={<DownloadIcon />}
                    onClick={handleDownload}
                    size="small"
                  >
                    Download PlantUML
                  </Button>
                </Box>
                
                <Paper
                  elevation={1}
                  sx={{
                    p: 2,
                    textAlign: 'center',
                    backgroundColor: '#fafafa',
                    border: '1px solid #e0e0e0',
                    borderRadius: 2
                  }}
                >
                  {getPlantUMLImageUrl() ? (
                    <>
                      <img 
                        src={getPlantUMLImageUrl()}
                        alt={`${diagramType} diagram`}
                        style={{ 
                          maxWidth: '100%', 
                          height: 'auto',
                          border: '1px solid #ddd',
                          borderRadius: '4px',
                          backgroundColor: 'white'
                        }}
                        onError={(e) => {
                          e.target.style.display = 'none';
                          setError('Failed to load diagram image. Please check the PlantUML code.');
                        }}
                      />
                      <Typography variant="caption" display="block" sx={{ mt: 2, color: 'text.secondary' }}>
                        Generated from RUPP Template SNL using OpenAI ChatGPT
                      </Typography>
                    </>
                  ) : (
                    <Alert severity="error">
                      Failed to generate diagram image. Please check the PlantUML code in the Code View tab.
                    </Alert>
                  )}
                </Paper>
              </Box>
            )}

            {/* Code View */}
            {viewMode === 1 && (
              <Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="subtitle1">
                    PlantUML Source Code
                  </Typography>
                  <Button
                    variant="outlined"
                    startIcon={<DownloadIcon />}
                    onClick={handleDownload}
                    size="small"
                  >
                    Download PlantUML
                  </Button>
                </Box>
                
                <Paper
                  elevation={1}
                  sx={{
                    p: 2,
                    backgroundColor: '#f5f5f5',
                    fontFamily: 'monospace',
                    fontSize: '0.875rem',
                    whiteSpace: 'pre-wrap',
                    maxHeight: 400,
                    overflow: 'auto',
                    border: '1px solid #e0e0e0'
                  }}
                >
                  {diagramData}
                </Paper>
                
                <Alert severity="info" sx={{ mt: 2 }}>
                  <Typography variant="body2">
                    Copy the PlantUML code above and paste it into{' '}
                    <a href="http://www.plantuml.com/plantuml/uml" target="_blank" rel="noopener noreferrer">
                      PlantUML Online Editor
                    </a>{' '}
                    for alternative visualization or editing.
                  </Typography>
                </Alert>
              </Box>
            )}
          </Box>
        )}

        {caseStudyData && !diagramData && !loading && (
          <Alert severity="info">
            Click one of the buttons above to generate a UML diagram from your processed requirements.
          </Alert>
        )}
      </Paper>
    </Box>
  );
};

export default DiagramViewer;
