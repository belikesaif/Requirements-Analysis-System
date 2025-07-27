import React, { useState, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Grid,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  Divider,
  Alert
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Clear as ClearIcon,
  Description as DescriptionIcon,
  AutoAwesome as AIIcon
} from '@mui/icons-material';

import { apiService } from '../services/apiService';
import { storageService } from '../services/storageService';

const RequirementsInput = ({ onProcessingComplete, onError, onSuccess }) => {
  const [inputText, setInputText] = useState('');
  const [title, setTitle] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = useRef(null);

  // Sample case study for demo
  const sampleCaseStudy = `The Member clicks the log-in button on the Home Page. The system displays the log-in page. The member enters his login Id with password and clicks the submit button. The system validates the member's Id and password. If the member is authenticated, then the system displays the Member home page. The member clicks the 'Search Books' button. The system displays the search page. The member enters the book title in the search field and clicks the search button. The system searches for the book in the database and displays the search results. If books are found, the system displays a list of matching books with details like title, author, and availability status.`;

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploadProgress(0);
    setIsProcessing(true);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await apiService.uploadFile(formData, (progressEvent) => {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        setUploadProgress(progress);
      });

      setInputText(response.content);
      setTitle(file.name.replace(/\.[^/.]+$/, "")); // Remove file extension
      setUploadProgress(100);
    } catch (error) {
      onError(`File upload failed: ${error.message}`);
    } finally {
      setIsProcessing(false);
      setUploadProgress(0);
    }
  };

  const handleProcessRequirements = async () => {
    if (!inputText.trim()) {
      onError('Please enter some requirements text');
      return;
    }

    setIsProcessing(true);

    try {
      const response = await apiService.processRequirements({
        text: inputText,
        title: title || 'Untitled Case Study'
      });

      // Store in local storage
      storageService.saveCaseStudy(response);

      onProcessingComplete(response);
    } catch (error) {
      onError(`Processing failed: ${error.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleLoadSample = () => {
    setInputText(sampleCaseStudy);
    setTitle('Library Management System - Login and Search');
  };

  const handleClear = () => {
    setInputText('');
    setTitle('');
  };

  const wordCount = inputText.trim().split(/\s+/).filter(word => word.length > 0).length;
  const sentenceCount = inputText.trim().split(/[.!?]+/).filter(sentence => sentence.trim().length > 0).length;

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Requirements Input
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Enter your natural language case study or upload a document file. The system will generate structured requirements using both RUPP's template methodology and AI analysis.
      </Typography>

      <Grid container spacing={3}>
        {/* Input Section */}
        <Grid item xs={12} md={8}>
          <Paper elevation={2} sx={{ p: 3 }}>
            <Box sx={{ mb: 2 }}>
              <TextField
                fullWidth
                label="Case Study Title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Enter a descriptive title for your case study"
                sx={{ mb: 2 }}
              />
              
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileUpload}
                  accept=".txt,.doc,.docx"
                  style={{ display: 'none' }}
                />
                <Button
                  variant="outlined"
                  startIcon={<UploadIcon />}
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isProcessing}
                >
                  Upload File
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<DescriptionIcon />}
                  onClick={handleLoadSample}
                  disabled={isProcessing}
                >
                  Load Sample
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<ClearIcon />}
                  onClick={handleClear}
                  disabled={isProcessing}
                >
                  Clear
                </Button>
              </Box>

              {uploadProgress > 0 && uploadProgress < 100 && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Uploading file... {uploadProgress}%
                  </Typography>
                  <LinearProgress variant="determinate" value={uploadProgress} />
                </Box>
              )}
            </Box>

            <TextField
              fullWidth
              multiline
              rows={12}
              label="Requirements Text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Enter your natural language case study here..."
              variant="outlined"
              disabled={isProcessing}
            />

            <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Chip 
                  label={`${wordCount} words`} 
                  size="small"
                  color={wordCount > 50 ? 'success' : 'default'}
                />
                <Chip 
                  label={`${sentenceCount} sentences`} 
                  size="small"
                  color={sentenceCount > 3 ? 'success' : 'default'}
                />
                {inputText.trim() && (
                  <Chip 
                    label={inputText.length > 200 ? "Good length" : "Too short"} 
                    size="small"
                    color={inputText.length > 200 ? 'success' : 'warning'}
                  />
                )}
              </Box>

              <Button
                variant="contained"
                size="large"
                startIcon={<AIIcon />}
                onClick={handleProcessRequirements}
                disabled={isProcessing || !inputText.trim() || inputText.length < 50}
                sx={{ minWidth: 180 }}
              >
                {isProcessing ? 'Processing...' : 'Process Requirements'}
              </Button>
            </Box>

            {inputText.length < 50 && inputText.length > 0 && (
              <Alert severity="info" sx={{ mt: 2 }}>
                Requirements text should be at least 50 characters for meaningful analysis.
              </Alert>
            )}

            {isProcessing && (
              <Box sx={{ mt: 2 }}>
                <LinearProgress />
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Generating RUPP template SNL and AI-based requirements...
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>

          <Grid item xs={12} md={4}>
            <Card elevation={2}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
            <AIIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            Processing Information
                </Typography>
                <Divider sx={{ mb: 2 }} />
                
                <Alert severity="info" sx={{ mb: 2 }}>
            The system will analyze your text using two approaches:
                </Alert>

                <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              1. RUPP's Template Method
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Uses predefined templates and rules to convert natural language into structured requirements following established patterns.
            </Typography>
                </Box>

                

                <Divider sx={{ my: 2 }} />

                <Typography variant="subtitle2" gutterBottom>
            RUPP Template Structure:
                </Typography>
                <Paper sx={{ p: 2, mb: 2, bgcolor: 'grey.50' }}>
            <Typography variant="body2" fontFamily="monospace" sx={{ mb: 1 }}>
              [&lt;When?&gt; &lt;under what conditions?&gt;]
            </Typography>
            <Typography variant="body2" fontFamily="monospace" sx={{ mb: 1 }}>
              THE SYSTEM &lt;system name&gt;
            </Typography>
            <Typography variant="body2" fontFamily="monospace" sx={{ mb: 1 }}>
              (SHALL | SHOULD | WILL)
            </Typography>
            <Typography variant="body2" fontFamily="monospace" sx={{ mb: 1 }}>
              (PROVIDE &lt;whom?&gt; WITH THE ABILITY TO &lt;process&gt;
            </Typography>
            <Typography variant="body2" fontFamily="monospace" sx={{ mb: 1 }}>
              | BE ABLE TO &lt;process&gt;)
            </Typography>
            <Typography variant="body2" fontFamily="monospace" sx={{ mb: 1 }}>
              &lt;object&gt;
            </Typography>
            <Typography variant="body2" fontFamily="monospace">
              [&lt;additional details about the object&gt;]
            </Typography>
                </Paper>

                <Typography variant="subtitle2" gutterBottom>
            Example:
                </Typography>
                <Paper sx={{ p: 2, mb: 2, bgcolor: 'primary.50', border: '1px solid', borderColor: 'primary.200' }}>
            <Typography variant="body2" sx={{ fontStyle: 'italic' }}>
              "When a member clicks the search button, the system shall provide the member with the ability to search books by title and display matching results with availability status."
            </Typography>
                </Paper>
                <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              2. AI-Powered Analysis
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Uses GPT-3.5 to generate structured natural language requirements with intelligent understanding of context.
            </Typography>
                </Box>

                <Typography variant="subtitle2" gutterBottom>
            Best Practices:
                </Typography>
                <Typography variant="body2" color="text.secondary" component="ul" sx={{ pl: 2 }}>
            <li>Write clear, complete sentences</li>
            <li>Include instances and actions explicitly</li>
            <li>Describe system responses</li>
            <li>Use conditional statements when appropriate</li>
                </Typography>
              </CardContent>
            </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default RequirementsInput;
