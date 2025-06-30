import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Tabs,
  Tab,
  CircularProgress,
  Alert,
  Switch,
  FormControlLabel
} from '@mui/material';
import { encode } from 'plantuml-encoder';

const PlantUMLViewer = ({ plantUMLCode, title = "UML Diagram", showCodeToggle = true }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [showCode, setShowCode] = useState(false);
  const [imageUrl, setImageUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

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
      // Clean the PlantUML code
      const cleanCode = plantUMLCode.trim();
      
      // Encode the PlantUML code
      const encoded = encode(cleanCode);
      
      // Use the PlantUML server to generate the diagram
      const url = `https://www.plantuml.com/plantuml/svg/${encoded}`;
      setImageUrl(url);
      
    } catch (err) {
      console.error('Error generating diagram:', err);
      setError('Failed to generate diagram. Please check the PlantUML syntax.');
    } finally {
      setIsLoading(false);
    }
  };

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
        <Typography variant="h6">{title}</Typography>
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
            <Alert severity="error" sx={{ width: '100%' }}>
              {error}
            </Alert>
          ) : imageUrl ? (
            <img
              src={imageUrl}
              alt="PlantUML Diagram"
              style={{
                maxWidth: '100%',
                maxHeight: '600px',
                objectFit: 'contain'
              }}
              onError={() => setError('Failed to load diagram image')}
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
