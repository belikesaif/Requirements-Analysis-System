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
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Paper,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Stepper,
  Step,
  StepLabel,
  StepContent
} from '@mui/material';
import {
  AutoAwesome as OptimizeIcon,
  PlayArrow as ProcessIcon,
  CheckCircle as SuccessIcon,
  TrendingUp as ImprovementIcon,
  Person as ActorIcon,
  BugReport as IssueIcon,
  Lightbulb as RecommendationIcon,
  ExpandMore as ExpandMoreIcon,
  CompareArrows as CompareIcon
} from '@mui/icons-material';
import PlantUMLViewer from './PlantUMLViewer';
import { apiService } from '../services/apiService';

const FinalLLMOptimizer = ({ 
  originalRequirements,
  classDiagram,
  sequenceDiagram,
  identifiedActors = [],
  verificationIssues = {},
  onOptimizationComplete,
  onError 
}) => {
  const [loading, setLoading] = useState(false);
  const [optimizedDiagrams, setOptimizedDiagrams] = useState(null);
  const [activeStep, setActiveStep] = useState(0);

  const handleFinalOptimization = async () => {
    if (!originalRequirements || !classDiagram || !sequenceDiagram) {
      onError('Missing required data for final optimization');
      return;
    }

    setLoading(true);
    setActiveStep(1);
    
    try {
      console.log('Performing final LLM optimization...');
      
      const response = await apiService.finalOptimization({
        original_requirements: originalRequirements,
        class_diagram: classDiagram,
        sequence_diagram: sequenceDiagram,
        identified_actors: identifiedActors,
        verification_issues: verificationIssues
      });

      setOptimizedDiagrams(response);
      setActiveStep(2);

      // Pass data to parent component
      if (onOptimizationComplete) {
        onOptimizationComplete(response);
      }

    } catch (error) {
      console.error('Final optimization error:', error);
      onError(error.message);
      setActiveStep(0);
    } finally {
      setLoading(false);
    }
  };

  const renderInputSummary = () => (
    <Card elevation={1} sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6" sx={{ mb: 2 }}>Optimization Inputs</Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'primary.light', color: 'primary.contrastText' }}>
              <Typography variant="h4">
                {originalRequirements ? '✓' : '✗'}
              </Typography>
              <Typography variant="body2">Original Requirements</Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'secondary.light', color: 'secondary.contrastText' }}>
              <Typography variant="h4">{identifiedActors.length}</Typography>
              <Typography variant="body2">Identified Actors</Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'warning.light', color: 'warning.contrastText' }}>
              <Typography variant="h4">
                {(verificationIssues.missing_actors?.length || 0) + (verificationIssues.inconsistencies?.length || 0)}
              </Typography>
              <Typography variant="body2">Issues to Fix</Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'info.light', color: 'info.contrastText' }}>
              <Typography variant="h4">2</Typography>
              <Typography variant="body2">Diagrams to Optimize</Typography>
            </Paper>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );

  const renderActorsAndIssues = () => (
    <Grid container spacing={3} sx={{ mb: 3 }}>
      {/* Identified Actors */}
      <Grid item xs={12} md={6}>
        <Card elevation={1}>
          <CardContent>
            <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <ActorIcon sx={{ mr: 1 }} />
              Actors to Include ({identifiedActors.length})
            </Typography>
            {identifiedActors.length > 0 ? (
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {identifiedActors.map((actor, index) => (
                  <Chip 
                    key={index}
                    label={actor}
                    variant="outlined"
                    color="primary"
                    size="small"
                  />
                ))}
              </Box>
            ) : (
              <Typography variant="body2" color="textSecondary">
                No specific actors identified
              </Typography>
            )}
          </CardContent>
        </Card>
      </Grid>

      {/* Issues to Address */}
      <Grid item xs={12} md={6}>
        <Card elevation={1}>
          <CardContent>
            <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <IssueIcon sx={{ mr: 1 }} />
              Issues to Address
            </Typography>
            
            {verificationIssues.missing_actors?.length > 0 && (
              <Alert severity="warning" sx={{ mb: 2 }}>
                <Typography variant="subtitle2">Missing Actors:</Typography>
                <Typography variant="body2">
                  {verificationIssues.missing_actors.join(', ')}
                </Typography>
              </Alert>
            )}

            {verificationIssues.inconsistencies?.length > 0 && (
              <Alert severity="error" sx={{ mb: 2 }}>
                <Typography variant="subtitle2">Inconsistencies:</Typography>
                <List dense>
                  {verificationIssues.inconsistencies.slice(0, 3).map((issue, index) => (
                    <ListItem key={index} sx={{ py: 0 }}>
                      <ListItemText 
                        primary={issue}
                        primaryTypographyProps={{ variant: 'body2' }}
                      />
                    </ListItem>
                  ))}
                </List>
              </Alert>
            )}

            {(!verificationIssues.missing_actors?.length && !verificationIssues.inconsistencies?.length) && (
              <Typography variant="body2" color="success.main">
                ✓ No major issues identified
              </Typography>
            )}
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderOptimizationProcess = () => (
    <Card elevation={2} sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6" sx={{ mb: 2 }}>Optimization Process</Typography>
        <Stepper activeStep={activeStep} orientation="vertical">
          <Step>
            <StepLabel>Ready for Optimization</StepLabel>
            <StepContent>
              <Typography variant="body2" color="textSecondary">
                All required inputs are prepared. GPT-3.5 will analyze and optimize both diagrams.
              </Typography>
            </StepContent>
          </Step>
          <Step>
            <StepLabel>Processing with GPT-3.5</StepLabel>
            <StepContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                {loading && <CircularProgress size={20} />}
                <Typography variant="body2" color="textSecondary">
                  {loading ? 'Analyzing requirements and optimizing diagrams...' : 'Optimization in progress'}
                </Typography>
              </Box>
            </StepContent>
          </Step>
          <Step>
            <StepLabel>Optimization Complete</StepLabel>
            <StepContent>
              <Typography variant="body2" color="textSecondary">
                Optimized diagrams generated with improvements applied.
              </Typography>
            </StepContent>
          </Step>
        </Stepper>
      </CardContent>
    </Card>
  );

  const renderOptimizedResults = () => {
    if (!optimizedDiagrams) return null;

    return (
      <Grid container spacing={3}>
        {/* Optimized Class Diagram */}
        <Grid item xs={12} md={6}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                <SuccessIcon sx={{ mr: 1, color: 'success.main' }} />
                Optimized Class Diagram
              </Typography>
              
              <PlantUMLViewer 
                plantUMLCode={optimizedDiagrams.optimized_class_diagram}
                title="Final Optimized Class Diagram"
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Optimized Sequence Diagram */}
        <Grid item xs={12} md={6}>
          <Card elevation={2}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                <SuccessIcon sx={{ mr: 1, color: 'success.main' }} />
                Optimized Sequence Diagram
              </Typography>
              
              <PlantUMLViewer 
                plantUMLCode={optimizedDiagrams.optimized_sequence_diagram}
                title="Final Optimized Sequence Diagram"
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Improvements Summary */}
        <Grid item xs={12}>
          <Card elevation={1}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
                <ImprovementIcon sx={{ mr: 1, color: 'primary.main' }} />
                Optimization Summary
              </Typography>
              
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle1" gutterBottom>
                    Applied Improvements:
                  </Typography>
                  <List dense>
                    {optimizedDiagrams.improvements?.map((improvement, index) => (
                      <ListItem key={index}>
                        <ListItemIcon>
                          <SuccessIcon fontSize="small" color="success" />
                        </ListItemIcon>
                        <ListItemText primary={improvement} />
                      </ListItem>
                    ))}
                  </List>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle1" gutterBottom>
                    Final Actors Included:
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {optimizedDiagrams.final_actors?.map((actor, index) => (
                      <Chip 
                        key={index}
                        label={actor}
                        color="success"
                        size="small"
                        icon={<ActorIcon />}
                      />
                    ))}
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Final Summary */}
        <Grid item xs={12}>
          <Alert severity="success">
            <Typography variant="h6" gutterBottom>
              🎉 Final Optimization Complete!
            </Typography>
            <Typography variant="body2">
              Both class and sequence diagrams have been optimized using GPT-3.5 with all identified actors, 
              original requirements, and verification feedback. The diagrams now represent a comprehensive 
              and consistent view of your system architecture.
            </Typography>
          </Alert>
        </Grid>
      </Grid>
    );
  };

  return (
    <Box sx={{ p: 3 }}>
      <Card elevation={2} sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <OptimizeIcon sx={{ mr: 2, color: 'primary.main' }} />
            <Typography variant="h5" component="h2">
              Screen 6: Final LLM Optimization
            </Typography>
          </Box>
          
          <Typography variant="body1" color="textSecondary" sx={{ mb: 3 }}>
            Final optimization using GPT-3.5 with all context: original requirements, identified actors, 
            initial diagrams, and verification feedback. This produces the definitive optimized diagrams.
          </Typography>

          <Alert severity="info" sx={{ mb: 3 }}>
            <Typography variant="body2">
              <strong>Optimization Context:</strong> Using original requirements + {identifiedActors.length} actors + 
              verification feedback + initial diagrams for comprehensive optimization.
            </Typography>
          </Alert>

          <Button
            variant="contained"
            size="large"
            startIcon={loading ? <CircularProgress size={16} /> : <ProcessIcon />}
            onClick={handleFinalOptimization}
            disabled={loading || !originalRequirements || !classDiagram || !sequenceDiagram}
            sx={{ mb: 2 }}
          >
            {loading ? 'Optimizing with GPT-3.5...' : 'Start Final Optimization'}
          </Button>
        </CardContent>
      </Card>

      {/* Input Summary */}
      {renderInputSummary()}

      {/* Actors and Issues */}
      {renderActorsAndIssues()}

      {/* Optimization Process */}
      {renderOptimizationProcess()}

      {/* Optimized Results */}
      {renderOptimizedResults()}

      {!optimizedDiagrams && !loading && (
        <Card elevation={1}>
          <CardContent sx={{ textAlign: 'center', py: 8 }}>
            <OptimizeIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="textSecondary" gutterBottom>
              Ready for Final Optimization
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Click "Start Final Optimization" to generate the definitive diagrams using all available context.
            </Typography>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default FinalLLMOptimizer;
