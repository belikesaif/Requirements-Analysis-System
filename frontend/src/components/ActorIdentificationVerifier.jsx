import React, { useState, useEffect } from 'react';
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
  LinearProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Person as ActorIcon,
  PlayArrow as IdentifyIcon,
  CheckCircle as SuccessIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  ExpandMore as ExpandMoreIcon,
  Visibility as ViewIcon,
  VerifiedUser as VerifyIcon
} from '@mui/icons-material';
import PlantUMLViewer from './PlantUMLViewer';
import DiagramRetryControls from './DiagramRetryControls';
import { apiService } from '../services/apiService';

const ActorIdentificationVerifier = ({ 
  originalRequirements,
  classDiagram,
  sequenceDiagram,
  onActorsIdentified,
  onError 
}) => {
  const [loading, setLoading] = useState(false);
  const [identifiedActors, setIdentifiedActors] = useState([]);
  const [verificationResults, setVerificationResults] = useState(null);
  const [expandedDiagram, setExpandedDiagram] = useState(null);

  const handleRetryComplete = (retryResult) => {
    console.log('Actor verification retry completed:', retryResult);
    
    // Update diagrams and re-run actor identification if needed
    // For now, we'll just update the diagrams
    setVerificationResults(prev => ({
      ...prev,
      updated_class_diagram: retryResult.classDiagram,
      updated_sequence_diagram: retryResult.sequenceDiagram,
      retry_info: {
        issue_type: retryResult.issueType,
        retry_count: retryResult.retryCount,
        improvements: retryResult.improvements
      }
    }));
  };

  const handleRetryError = (error) => {
    console.error('Actor verification retry error:', error);
    onError?.(error);
  };

  const handleIdentifyActors = async () => {
    if (!originalRequirements) {
      onError('Original requirements are required for actor identification');
      return;
    }

    // Allow the process to continue even without diagrams, but warn the user
    if (!classDiagram && !sequenceDiagram) {
      onError('At least one diagram (class or sequence) is required for verification');
      return;
    }

    setLoading(true);
    try {
      console.log('Identifying actors from requirements and diagrams...');
      console.log('Requirements available:', !!originalRequirements);
      console.log('Class diagram available:', !!classDiagram);
      console.log('Sequence diagram available:', !!sequenceDiagram);
      
      const response = await apiService.identifyActors({
        original_requirements: originalRequirements,
        class_diagram: classDiagram || '',
        sequence_diagram: sequenceDiagram || ''
      });

      setIdentifiedActors(response.identified_actors || []);
      setVerificationResults(response.verification_results || {});

      // Pass data to parent component
      if (onActorsIdentified) {
        onActorsIdentified({
          actors: response.identified_actors,
          verification: response.verification_results
        });
      }

    } catch (error) {
      console.error('Actor identification error:', error);
      onError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const getVerificationScore = () => {
    if (!verificationResults) return 0;
    return Math.round((verificationResults.overall_score || 0) * 100);
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'error';
  };

  const renderActorsList = () => {
    if (!identifiedActors.length) return null;

    return (
      <Card elevation={1} sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
            <ActorIcon sx={{ mr: 1 }} />
            Identified Actors ({identifiedActors.length})
          </Typography>
          
          <Grid container spacing={1}>
            {identifiedActors.map((actor, index) => (
              <Grid item key={index}>
                <Chip 
                  label={actor}
                  variant="outlined"
                  color="primary"
                  icon={<ActorIcon />}
                />
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>
    );
  };

  const renderVerificationResults = () => {
    if (!verificationResults) return null;

    const score = getVerificationScore();
    const scoreColor = getScoreColor(score);

    return (
      <Grid container spacing={3}>
        {/* Overall Score */}
        <Grid item xs={12} md={4}>
          <Card elevation={1}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h6" gutterBottom>
                Verification Score
              </Typography>
              <Box sx={{ position: 'relative', display: 'inline-flex', mb: 2 }}>
                <CircularProgress
                  variant="determinate"
                  value={score}
                  size={80}
                  thickness={4}
                  color={scoreColor}
                />
                <Box sx={{
                  top: 0,
                  left: 0,
                  bottom: 0,
                  right: 0,
                  position: 'absolute',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}>
                  <Typography variant="h6" component="div" color={`${scoreColor}.main`}>
                    {score}%
                  </Typography>
                </Box>
              </Box>
              <Typography variant="body2" color="textSecondary">
                Overall diagram-actor alignment
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Missing Actors */}
        <Grid item xs={12} md={4}>
          <Card elevation={1}>
            <CardContent>
              <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <WarningIcon sx={{ mr: 1, color: 'warning.main' }} />
                Missing Actors
              </Typography>
              {verificationResults.missing_actors?.length > 0 ? (
                <List dense>
                  {verificationResults.missing_actors.map((actor, index) => (
                    <ListItem key={index} sx={{ py: 0.5 }}>
                      <ListItemIcon sx={{ minWidth: 32 }}>
                        <ErrorIcon fontSize="small" color="error" />
                      </ListItemIcon>
                      <ListItemText primary={actor} />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography variant="body2" color="success.main">
                  ✓ All actors are represented in diagrams
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Present Actors */}
        <Grid item xs={12} md={4}>
          <Card elevation={1}>
            <CardContent>
              <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <SuccessIcon sx={{ mr: 1, color: 'success.main' }} />
                Present Actors
              </Typography>
              {verificationResults.present_actors?.length > 0 ? (
                <List dense>
                  {verificationResults.present_actors.map((actor, index) => (
                    <ListItem key={index} sx={{ py: 0.5 }}>
                      <ListItemIcon sx={{ minWidth: 32 }}>
                        <SuccessIcon fontSize="small" color="success" />
                      </ListItemIcon>
                      <ListItemText primary={actor} />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography variant="body2" color="textSecondary">
                  No actors found in diagrams
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Inconsistencies */}
        {verificationResults.inconsistencies?.length > 0 && (
          <Grid item xs={12}>
            <Alert severity="warning" sx={{ mb: 2 }}>
              <Typography variant="h6" gutterBottom>Identified Issues:</Typography>
              <List dense>
                {verificationResults.inconsistencies.map((issue, index) => (
                  <ListItem key={index} sx={{ py: 0.5 }}>
                    <ListItemText primary={issue} />
                  </ListItem>
                ))}
              </List>
            </Alert>
          </Grid>
        )}

        {/* Recommendations */}
        {verificationResults.recommendations?.length > 0 && (
          <Grid item xs={12}>
            <Alert severity="info">
              <Typography variant="h6" gutterBottom>Recommendations:</Typography>
              <List dense>
                {verificationResults.recommendations.map((rec, index) => (
                  <ListItem key={index} sx={{ py: 0.5 }}>
                    <ListItemText primary={rec} />
                  </ListItem>
                ))}
              </List>
            </Alert>
          </Grid>
        )}
      </Grid>
    );
  };

  return (
    <Box sx={{ p: 3 }}>
      <Card elevation={2} sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <VerifyIcon sx={{ mr: 2, color: 'primary.main' }} />
            <Typography variant="h5" component="h2">
              Screen 5: Actor Identification & Verification
            </Typography>
          </Box>
          
          <Typography variant="body1" color="textSecondary" sx={{ mb: 3 }}>
            Extract actors from original requirements using POS tagging and NER, then verify 
            against the generated diagrams to identify missing or inconsistent elements.
          </Typography>

          <Alert severity="info" sx={{ mb: 3 }}>
            <Typography variant="body2">
              <strong>Analysis Method:</strong> Using spaCy NER + POS tagging + GPT-3.5 for comprehensive actor extraction.<br/>
              <strong>Verification:</strong> Cross-referencing identified actors with diagram elements.<br/>
              <strong>Status:</strong> 
              {originalRequirements ? `✓ Requirements available (${originalRequirements.length} chars)` : '✗ Requirements missing'} | 
              {classDiagram ? `✓ Class diagram available (${classDiagram.length} chars)` : '✗ Class diagram missing'} | 
              {sequenceDiagram ? `✓ Sequence diagram available (${sequenceDiagram.length} chars)` : '✗ Sequence diagram missing'}
            </Typography>
            {(!originalRequirements || (!classDiagram && !sequenceDiagram)) && (
              <Typography variant="body2" color="warning.main" sx={{ mt: 1 }}>
                ⚠️ Missing data detected. Please ensure you've completed the previous steps.
              </Typography>
            )}
          </Alert>

          <Button
            variant="contained"
            size="large"
            startIcon={loading ? <CircularProgress size={16} /> : <IdentifyIcon />}
            onClick={handleIdentifyActors}
            disabled={loading || !originalRequirements || (!classDiagram && !sequenceDiagram)}
            sx={{ mb: 2 }}
          >
            {loading ? 'Identifying Actors...' : 'Identify Actors & Verify'}
          </Button>

          {(!classDiagram || !sequenceDiagram) && (
            <Alert severity="warning" sx={{ mt: 2 }}>
              <Typography variant="body2">
                {!classDiagram && !sequenceDiagram ? 
                  'Both class and sequence diagrams are missing. Actor identification will work with requirements only.' :
                  !classDiagram ? 
                    'Class diagram is missing. Verification will be limited to sequence diagram.' :
                    'Sequence diagram is missing. Verification will be limited to class diagram.'
                }
              </Typography>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Actors List */}
      {renderActorsList()}

      {/* Verification Results */}
      {verificationResults && (
        <Card elevation={2} sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 3 }}>Verification Results</Typography>
            {renderVerificationResults()}
          </CardContent>
        </Card>
      )}

      {/* Diagram Review Section */}
      {(classDiagram || sequenceDiagram) && (
        <>
          {/* Retry Controls for Diagrams */}
          {identifiedActors.length > 0 && (
            <DiagramRetryControls
              originalRequirements={originalRequirements}
              classDiagram={classDiagram}
              sequenceDiagram={sequenceDiagram}
              identifiedActors={identifiedActors}
              onRetryComplete={handleRetryComplete}
              onError={handleRetryError}
              disabled={loading}
            />
          )}

          <Card elevation={1}>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2 }}>Diagram Review</Typography>
            <Typography variant="body2" color="textSecondary" sx={{ mb: 3 }}>
              Review the generated diagrams to understand how actors are represented.
            </Typography>

            <Grid container spacing={2}>
              {classDiagram && (
                <Grid item xs={12} md={6}>
                  <Accordion>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography variant="subtitle1">
                        Class Diagram Review
                      </Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <PlantUMLViewer 
                        plantUMLCode={classDiagram}
                        title="Generated Class Diagram"
                      />
                    </AccordionDetails>
                  </Accordion>
                </Grid>
              )}

              {sequenceDiagram && (
                <Grid item xs={12} md={6}>
                  <Accordion>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography variant="subtitle1">
                        Sequence Diagram Review
                      </Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                      <PlantUMLViewer 
                        plantUMLCode={sequenceDiagram}
                        title="Generated Sequence Diagram"
                      />
                    </AccordionDetails>
                  </Accordion>
                </Grid>
              )}
            </Grid>
          </CardContent>
        </Card>
        </>
      )}

      {!identifiedActors.length && !loading && (
        <Card elevation={1}>
          <CardContent sx={{ textAlign: 'center', py: 8 }}>
            <ActorIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="textSecondary" gutterBottom>
              No Actors Identified Yet
            </Typography>
            <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
              Click "Identify Actors & Verify" to extract actors from requirements and verify diagram consistency.
            </Typography>
            {!originalRequirements && (
              <Alert severity="error" sx={{ mt: 2, textAlign: 'left' }}>
                <Typography variant="body2">
                  <strong>Missing Requirements:</strong> Please go back to Screen 1 to input requirements first.
                </Typography>
              </Alert>
            )}
            {!classDiagram && !sequenceDiagram && originalRequirements && (
              <Alert severity="warning" sx={{ mt: 2, textAlign: 'left' }}>
                <Typography variant="body2">
                  <strong>Missing Diagrams:</strong> Please go back to Screen 4 to generate diagrams first, or proceed with requirements-only actor identification.
                </Typography>
              </Alert>
            )}
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default ActorIdentificationVerifier;
