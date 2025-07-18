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
        <Grid item xs={12} md={3}>
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

        {/* Statistics Summary */}
        <Grid item xs={12} md={3}>
          <Card elevation={1}>
            <CardContent sx={{ textAlign: 'center' }}>
              <Typography variant="h6" gutterBottom>
                Coverage Statistics
              </Typography>
              <Typography variant="h4" color="primary.main" gutterBottom>
                {verificationResults.statistics?.coverage_percentage?.toFixed(1) || 0}%
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                Actor Coverage
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {verificationResults.statistics?.present_count || 0} of {verificationResults.statistics?.total_identified_actors || 0} actors present
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Missing Actors */}
        <Grid item xs={12} md={3}>
          <Card elevation={1}>
            <CardContent>
              <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <WarningIcon sx={{ mr: 1, color: 'warning.main' }} />
                Missing Actors ({verificationResults.missing_actors?.length || 0})
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

        {/* Overspecified Classes */}
        <Grid item xs={12} md={3}>
          <Card elevation={1}>
            <CardContent>
              <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <InfoIcon sx={{ mr: 1, color: 'info.main' }} />
                Overspecified Classes ({verificationResults.overspecified_classes?.length || 0})
              </Typography>
              {verificationResults.overspecified_classes?.length > 0 ? (
                <List dense>
                  {verificationResults.overspecified_classes.map((cls, index) => (
                    <ListItem key={index} sx={{ py: 0.5 }}>
                      <ListItemIcon sx={{ minWidth: 32 }}>
                        <InfoIcon fontSize="small" color="info" />
                      </ListItemIcon>
                      <ListItemText primary={cls} />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography variant="body2" color="success.main">
                  ✓ No overspecified classes detected
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Incorrect Classes */}
        <Grid item xs={12} md={3}>
          <Card elevation={1}>
            <CardContent>
              <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <ErrorIcon sx={{ mr: 1, color: 'error.main' }} />
                Incorrect Actors ({verificationResults.incorrect_classes?.length || 0})
              </Typography>
              {verificationResults.incorrect_classes?.length > 0 ? (
                <List dense>
                  {verificationResults.incorrect_classes.map((cls, index) => (
                    <ListItem key={index} sx={{ py: 0.5 }}>
                      <ListItemIcon sx={{ minWidth: 32 }}>
                        <ErrorIcon fontSize="small" color="error" />
                      </ListItemIcon>
                      <ListItemText primary={cls} secondary="Generic or inappropriate" />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography variant="body2" color="success.main">
                  ✓ No incorrect actors detected
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Present Actors */}
        <Grid item xs={12} md={9}>
          <Card elevation={1}>
            <CardContent>
              <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <SuccessIcon sx={{ mr: 1, color: 'success.main' }} />
                Present Actors ({verificationResults.present_actors?.length || 0})
              </Typography>
              {verificationResults.present_actors?.length > 0 ? (
                <Grid container spacing={1}>
                  {verificationResults.present_actors.map((actor, index) => (
                    <Grid item key={index}>
                      <Chip 
                        label={actor}
                        color="success"
                        size="small"
                        icon={<SuccessIcon />}
                      />
                    </Grid>
                  ))}
                </Grid>
              ) : (
                <Typography variant="body2" color="textSecondary">
                  No actors found in diagrams
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Detailed Statistics */}
        {verificationResults.statistics && (
          <Grid item xs={12}>
            <Card elevation={1}>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>Detailed Analysis Statistics</Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6} sm={3}>
                    <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'primary.light', color: 'primary.contrastText' }}>
                      <Typography variant="h4">{verificationResults.statistics.total_identified_actors}</Typography>
                      <Typography variant="body2">Identified Actors</Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'success.light', color: 'success.contrastText' }}>
                      <Typography variant="h4">{verificationResults.statistics.present_count}</Typography>
                      <Typography variant="body2">Present in Diagrams</Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'warning.light', color: 'warning.contrastText' }}>
                      <Typography variant="h4">{verificationResults.statistics.missing_count}</Typography>
                      <Typography variant="body2">Missing from Diagrams</Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'info.light', color: 'info.contrastText' }}>
                      <Typography variant="h4">{verificationResults.statistics.overspecified_count}</Typography>
                      <Typography variant="body2">Overspecified Classes</Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'error.light', color: 'error.contrastText' }}>
                      <Typography variant="h4">{verificationResults.incorrect_classes?.length || 0}</Typography>
                      <Typography variant="body2">Incorrect Actors</Typography>
                    </Paper>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        )}

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

        {/* Incorrect Actors Alert */}
        {verificationResults.incorrect_classes?.length > 0 && (
          <Grid item xs={12}>
            <Alert severity="error" sx={{ mb: 2 }}>
              <Typography variant="h6" gutterBottom>Incorrect Actors Detected:</Typography>
              <Typography variant="body2" gutterBottom>
                The following actors in your diagrams are considered incorrect or too generic. 
                They should be replaced with more specific, domain-relevant actors:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
                {verificationResults.incorrect_classes.map((cls, index) => (
                  <Chip 
                    key={index}
                    label={cls}
                    color="error"
                    size="small"
                    variant="outlined"
                    icon={<ErrorIcon />}
                  />
                ))}
              </Box>
            </Alert>
          </Grid>
        )}

        {/* Overspecification Alert */}
        {verificationResults.overspecified_classes?.length > 0 && (
          <Grid item xs={12}>
            <Alert severity="info" sx={{ mb: 2 }}>
              <Typography variant="h6" gutterBottom>Overspecified Classes Detected:</Typography>
              <Typography variant="body2" gutterBottom>
                The following classes appear in your diagrams but were not identified from the requirements. 
                Consider if they are necessary or if they add unnecessary complexity:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
                {verificationResults.overspecified_classes.map((cls, index) => (
                  <Chip 
                    key={index}
                    label={cls}
                    color="info"
                    size="small"
                    variant="outlined"
                  />
                ))}
              </Box>
            </Alert>
          </Grid>
        )}

        {/* Specification Issues */}
        {verificationResults.specification_issues?.length > 0 && (
          <Grid item xs={12}>
            <Alert severity="error" sx={{ mb: 2 }}>
              <Typography variant="h6" gutterBottom>Specification Issues:</Typography>
              <List dense>
                {verificationResults.specification_issues.map((issue, index) => (
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
              <strong>Verification:</strong> Cross-referencing identified actors with diagram elements + overspecification detection.<br/>
              <strong>Detection:</strong> Missing actors, overspecified classes, incorrect classes, and specification issues.<br/>
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
            {loading ? 'Analyzing Actors & Diagrams...' : 'Identify Actors & Verify Diagrams'}
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
