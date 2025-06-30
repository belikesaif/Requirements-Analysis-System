import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  CircularProgress,
  Alert,
  Fade,
  Divider,
  Chip
} from '@mui/material';
import {
  AutoAwesome as OptimizeIcon,
  Description as RuppIcon
} from '@mui/icons-material';

import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';

const OptimizationRequest = ({ ruppSnlData, onOptimize, onError }) => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [showRupp, setShowRupp] = useState(false);

  const handleOptimizeClick = async () => {
    if (!onOptimize) {
      onError('onOptimize function is not provided');
      return;
    }

    setIsProcessing(true);
    try {
      // Simulate processing time (2-3 seconds)
      await new Promise(resolve => setTimeout(resolve, 2500));
      
      // Show RUPP template
      setShowRupp(true);
      
      // Wait a bit more before completing
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Call parent handler with optimization results
      const optimizationResults = {
        optimized_requirements: ruppSnlData.formatted_sentences || ruppSnlData.snl_text,
        metrics: ruppSnlData.metrics || {},
        timestamp: new Date().toISOString(),
        status: 'completed'
      };
      
      onOptimize(optimizationResults);
    } catch (error) {
      onError(`Optimization failed: ${error.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  if (!ruppSnlData) {
    return (
      <Box>
        <Typography variant="h4" gutterBottom>
          RUPP Template Optimization
        </Typography>
        <Alert severity="info">
          No RUPP template data available for optimization.
        </Alert>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        RUPP Template Optimization
      </Typography>

      <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <RuppIcon sx={{ mr: 1 }} />
            <Typography variant="h6">
              RUPP Template Processing
            </Typography>
            {/* Only show requirements count AFTER optimization starts */}
            {showRupp && (
              <Chip 
                label={`${ruppSnlData.sentences_count || 0} requirements processed`}
                size="small"
                sx={{ ml: 2 }}
                color="success"
              />
            )}
          </Box>
          
          <Button
            variant="contained"
            startIcon={isProcessing ? <CircularProgress size={20} /> : <OptimizeIcon />}
            onClick={handleOptimizeClick}
            disabled={isProcessing}
          >
            {isProcessing ? 'Optimizing...' : 'Optimize Requirements'}
          </Button>
        </Box>

        <Divider sx={{ mb: 2 }} />

        {!showRupp && !isProcessing && (
          <Alert severity="info" sx={{ minHeight: '200px', display: 'flex', alignItems: 'center' }}>
            <Box>
              <Typography variant="h6" gutterBottom>Ready for Optimization</Typography>
              <Typography variant="body2">
                Click "Optimize Requirements" to process your requirements using the RUPP template methodology.
                This will generate structured, validated requirements based on industry standards.
              </Typography>
            </Box>
          </Alert>
        )}

        <Fade in={showRupp} timeout={1000}>
          <Box>
            <SyntaxHighlighter 
              language="text"
              style={oneLight}
              customStyle={{
                fontSize: '14px',
                lineHeight: '1.4',
                padding: '20px',
                borderRadius: '4px',
                backgroundColor: '#fafafa'
              }}
            >
              {ruppSnlData.formatted_sentences || ruppSnlData.snl_text}
            </SyntaxHighlighter>

            {ruppSnlData.metrics && (
              <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                <Chip 
                  label={`Precision: ${((ruppSnlData.metrics.precision || 0) * 100).toFixed(1)}%`}
                  size="small"
                  color="primary"
                />
                <Chip 
                  label={`Recall: ${((ruppSnlData.metrics.recall || 0) * 100).toFixed(1)}%`}
                  size="small"
                  color="secondary"
                />
                <Chip 
                  label={`F1 Score: ${((ruppSnlData.metrics.f1_score || 0) * 100).toFixed(1)}%`}
                  size="small"
                />
              </Box>
            )}
          </Box>
        </Fade>

        {isProcessing && !showRupp && (
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', py: 4 }}>
            <CircularProgress size={24} sx={{ mr: 2 }} />
            <Typography>Processing optimization request...</Typography>
          </Box>
        )}
      </Paper>
    </Box>
  );
};

export default OptimizationRequest; 