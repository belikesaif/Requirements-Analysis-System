import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Divider,
  Chip,
  Alert,
  LinearProgress,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon
} from '@mui/material';
import {
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  GetApp as ExportIcon
} from '@mui/icons-material';

import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';

const SNLComparison = ({ caseStudyData, onError }) => {
  const [selectedRequirement, setSelectedRequirement] = useState(null);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [expandedSection, setExpandedSection] = useState(false);

  const handleRequirementClick = (requirement, type) => {
    setSelectedRequirement({ requirement, type });
    setDetailsDialogOpen(true);
  };

  const handleCloseDetails = () => {
    setDetailsDialogOpen(false);
    setSelectedRequirement(null);
  };

  const handleAccordionChange = (panel) => (event, isExpanded) => {
    setExpandedSection(isExpanded ? panel : false);
  };

  const exportComparison = () => {
    try {
      const exportData = {
        caseStudy: caseStudyData,
        exportDate: new Date().toISOString(),
        summary: caseStudyData.comparison?.summary || {}
      };

      const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      
      const a = document.createElement('a');
      a.href = url;
      a.download = `snl-comparison-${Date.now()}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      onError('Failed to export comparison data');
    }
  };

  if (!caseStudyData || !caseStudyData.comparison) {
    return (
      <Alert severity="warning">
        No comparison data available. Please process a case study first.
      </Alert>
    );  }

  const { rupp_snl, ai_snl, comparison } = caseStudyData;
  const { metrics, categorization, summary } = comparison;

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          SNL Comparison Analysis
        </Typography>
        <Button
          variant="outlined"
          startIcon={<ExportIcon />}
          onClick={exportComparison}
        >
          Export Results
        </Button>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Overall Accuracy
              </Typography>
              <Typography variant="h4" color="primary">
                {((metrics?.accuracy || 0) * 100).toFixed(1)}%
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={(metrics?.accuracy || 0) * 100} 
                sx={{ mt: 1 }}
              />
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Precision Score
              </Typography>
              <Typography variant="h4" color="secondary">
                {((metrics?.precision || 0) * 100).toFixed(1)}%
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={(metrics?.precision || 0) * 100} 
                color="secondary"
                sx={{ mt: 1 }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Recall Score
              </Typography>
              <Typography variant="h4" style={{ color: '#ff9800' }}>
                {((metrics?.recall || 0) * 100).toFixed(1)}%
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={(metrics?.recall || 0) * 100} 
                sx={{ mt: 1, '& .MuiLinearProgress-bar': { backgroundColor: '#ff9800' } }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card elevation={2}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Quality Assessment
              </Typography>
              <Typography variant="h5">
                {summary?.quality_assessment || 'Unknown'}
              </Typography>
              <Chip 
                label={`F1: ${((metrics?.f1_score || 0) * 100).toFixed(1)}%`}
                size="small"
                sx={{ mt: 1 }}
              />
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Detailed Analysis */}
      <Grid container spacing={3}>
        {/* RUPP SNL */}
        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 3, height: 'fit-content' }}>
            <Typography variant="h6" gutterBottom>
              RUPP Template SNL
              <Chip 
                label={`${rupp_snl?.sentences_count || 0} requirements`}
                size="small"
                sx={{ ml: 1 }}
              />
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
              {rupp_snl?.formatted_sentences ? (
                <SyntaxHighlighter 
                  language="text" 
                  style={oneLight}
                  customStyle={{ fontSize: '14px', lineHeight: '1.4' }}
                >
                  {rupp_snl.formatted_sentences}
                </SyntaxHighlighter>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No RUPP SNL data available
                </Typography>
              )}
            </Box>

            {rupp_snl?.actors && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Identified Actors:
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {rupp_snl.actors.map((actor, index) => (
                    <Chip key={index} label={actor} size="small" variant="outlined" />
                  ))}
                </Box>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* AI SNL */}
        <Grid item xs={12} md={6}>
          <Paper elevation={2} sx={{ p: 3, height: 'fit-content' }}>
            <Typography variant="h6" gutterBottom>
              AI-Generated SNL
              <Chip 
                label={`${ai_snl?.sentences_count || 0} requirements`}
                size="small"
                sx={{ ml: 1 }}
              />
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
              {ai_snl?.requirements ? (
                <List dense>
                  {ai_snl.requirements.map((req, index) => (
                    <ListItem 
                      key={index}
                      button
                      onClick={() => handleRequirementClick(req, 'ai')}
                      sx={{ border: '1px solid #e0e0e0', mb: 1, borderRadius: 1 }}
                    >
                      <ListItemText 
                        primary={`${index + 1}. ${req}`}
                        primaryTypographyProps={{ variant: 'body2' }}
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No AI SNL data available
                </Typography>
              )}
            </Box>

            {ai_snl?.model_used && (
              <Box sx={{ mt: 2 }}>
                <Chip 
                  label={`Model: ${ai_snl.model_used}`}
                  size="small"
                  color="primary"
                  variant="outlined"
                />
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Categorization Analysis */}
      <Paper elevation={2} sx={{ mt: 3, p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Difference Analysis
        </Typography>
        <Divider sx={{ mb: 2 }} />

        <Grid container spacing={3}>
          {/* Missing Requirements */}
          <Grid item xs={12} md={6} lg={3}>
            <Card variant="outlined" sx={{ borderColor: 'error.main' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <ErrorIcon color="error" sx={{ mr: 1 }} />
                  <Typography variant="h6" color="error">
                    Missing ({categorization?.missing?.length || 0})
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Requirements in RUPP but not in AI
                </Typography>
                
                {categorization?.missing?.slice(0, 3).map((item, index) => (
                  <Alert key={index} severity="error" sx={{ mt: 1, fontSize: '0.75rem' }}>
                    {item.requirement?.substring(0, 50)}...
                  </Alert>
                ))}
                
                {(categorization?.missing?.length || 0) > 3 && (
                  <Typography variant="caption" color="text.secondary">
                    +{categorization.missing.length - 3} more
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Overspecified Requirements */}
          <Grid item xs={12} md={6} lg={3}>
            <Card variant="outlined" sx={{ borderColor: 'warning.main' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <WarningIcon color="warning" sx={{ mr: 1 }} />
                  <Typography variant="h6" color="warning.main">
                    Overspecified ({categorization?.overspecified?.length || 0})
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Extra requirements in AI
                </Typography>
                
                {categorization?.overspecified?.slice(0, 3).map((item, index) => (
                  <Alert key={index} severity="warning" sx={{ mt: 1, fontSize: '0.75rem' }}>
                    {item.requirement?.substring(0, 50)}...
                  </Alert>
                ))}
                
                {(categorization?.overspecified?.length || 0) > 3 && (
                  <Typography variant="caption" color="text.secondary">
                    +{categorization.overspecified.length - 3} more
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Out of Scope */}
          <Grid item xs={12} md={6} lg={3}>
            <Card variant="outlined" sx={{ borderColor: 'info.main' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <InfoIcon color="info" sx={{ mr: 1 }} />
                  <Typography variant="h6" color="info.main">
                    Out of Scope ({categorization?.out_of_scope?.length || 0})
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Not in original case study
                </Typography>
                
                {categorization?.out_of_scope?.slice(0, 3).map((item, index) => (
                  <Alert key={index} severity="info" sx={{ mt: 1, fontSize: '0.75rem' }}>
                    {item.requirement?.substring(0, 50)}...
                  </Alert>
                ))}
                
                {(categorization?.out_of_scope?.length || 0) > 3 && (
                  <Typography variant="caption" color="text.secondary">
                    +{categorization.out_of_scope.length - 3} more
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Matched Requirements */}
          <Grid item xs={12} md={6} lg={3}>
            <Card variant="outlined" sx={{ borderColor: 'success.main' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <CheckIcon color="success" sx={{ mr: 1 }} />
                  <Typography variant="h6" color="success.main">
                    Matched ({categorization?.matched?.length || 0})
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Successfully aligned requirements
                </Typography>
                
                <Box sx={{ mt: 2 }}>
                  <Typography variant="h4" color="success.main">
                    {categorization?.matched?.length || 0}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    requirements matched
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Paper>

      {/* Recommendations */}
      {summary?.recommendations && summary.recommendations.length > 0 && (
        <Paper elevation={2} sx={{ mt: 3, p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Recommendations
          </Typography>
          <Divider sx={{ mb: 2 }} />
          
          <List>
            {summary.recommendations.map((recommendation, index) => (
              <ListItem key={index}>
                <ListItemIcon>
                  <InfoIcon color="primary" />
                </ListItemIcon>
                <ListItemText primary={recommendation} />
              </ListItem>
            ))}
          </List>
        </Paper>
      )}

      {/* Requirement Details Dialog */}
      <Dialog
        open={detailsDialogOpen}
        onClose={handleCloseDetails}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          Requirement Details
        </DialogTitle>
        <DialogContent>
          {selectedRequirement && (
            <Box>
              <Typography variant="subtitle1" gutterBottom>
                Type: {selectedRequirement.type === 'ai' ? 'AI-Generated' : 'RUPP Template'}
              </Typography>
              <Typography variant="body1" sx={{ mt: 2 }}>
                {selectedRequirement.requirement}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDetails}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SNLComparison;
