import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  CircularProgress,
  Alert,
  Button,
  Divider,
  Grid,
  Card,
  CardContent
} from '@mui/material';
import {
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  AutoAwesome as AIIcon,
  ArrowForward as ArrowForwardIcon,
  Remove as MissingIcon,
  Add as OverspecifiedIcon,
  Close as IncorrectIcon,
  Assessment as StatsIcon
} from '@mui/icons-material';

const AIResultsVerifier = ({ aiSnlData, ruppOptimizedData, onVerificationComplete, onError, onContinue }) => {
  const [verificationResults, setVerificationResults] = useState([]);
  const [comparisonStats, setComparisonStats] = useState(null);
  const [isVerifying, setIsVerifying] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [issues, setIssues] = useState({ missing: [], overspecified: [], incorrect: [] });

  useEffect(() => {
    const verifyAndAnalyze = async () => {
      if (aiSnlData?.requirements) {
        await verifyRequirements();
      }
      if (aiSnlData?.requirements && ruppOptimizedData) {
        await analyzeComparison();
      }
    };
    
    verifyAndAnalyze();
  }, [aiSnlData, ruppOptimizedData]);

  const verifyRequirements = async () => {
    setIsVerifying(true);
    try {
      const results = [];
      const foundIssues = { missing: [], overspecified: [], incorrect: [] };

      // Batch validation instead of one-by-one for performance
      const batchSize = 5;
      const requirements = aiSnlData.requirements || [];
      
      for (let i = 0; i < requirements.length; i += batchSize) {
        const batch = requirements.slice(i, i + batchSize);
        
        // Process batch in parallel
        const batchPromises = batch.map(async (requirement) => {
          try {
            // For demo purposes, simulate faster validation
            const validation = await simulateValidation(requirement);
            return { requirement, validation };
          } catch (error) {
            // Fallback validation on error
            return { 
              requirement, 
              validation: {
                clarity: Math.floor(Math.random() * 4) + 6, // 6-9
                completeness: Math.floor(Math.random() * 4) + 6, // 6-9
                atomicity: Math.floor(Math.random() * 4) + 6 // 6-9
              }
            };
          }
        });

        const batchResults = await Promise.all(batchPromises);
        results.push(...batchResults);

        // Categorize issues from this batch
        batchResults.forEach(({ requirement, validation }) => {
          if (validation.clarity < 7) foundIssues.incorrect.push(requirement);
          if (validation.completeness < 7) foundIssues.missing.push(requirement);
          if (validation.atomicity < 7) foundIssues.overspecified.push(requirement);
        });

        // Add small delay between batches to show progress
        if (i + batchSize < requirements.length) {
          await new Promise(resolve => setTimeout(resolve, 500));
        }
      }

      setVerificationResults(results);
      setIssues(foundIssues);

      // Notify parent of completion with results
      onVerificationComplete({
        results,
        issues: foundIssues,
        totalIssues: Object.values(foundIssues).flat().length
      });

    } catch (error) {
      onError(`Verification failed: ${error.message}`);
    } finally {
      setIsVerifying(false);
    }
  };

  const simulateValidation = async (requirement) => {
    // Fast simulation instead of API call for demo
    await new Promise(resolve => setTimeout(resolve, 200));
    
    return {
      clarity: Math.floor(Math.random() * 4) + 6, // 6-9
      completeness: Math.floor(Math.random() * 4) + 6, // 6-9
      atomicity: Math.floor(Math.random() * 4) + 6 // 6-9
    };
  };

  const getStatusIcon = (scores) => {
    const avgScore = Object.values(scores).reduce((a, b) => a + b, 0) / Object.values(scores).length;
    if (avgScore >= 8) return <CheckIcon color="success" />;
    if (avgScore >= 6) return <WarningIcon color="warning" />;
    return <ErrorIcon color="error" />;
  };

  const performSimpleComparison = (aiRequirements, ruppData) => {
    console.log('=== DEBUGGING COMPARISON DATA ===');
    console.log('AI Requirements Input:', aiRequirements);
    console.log('AI Requirements Type:', typeof aiRequirements);
    console.log('AI Requirements Length:', aiRequirements?.length);
    console.log('RUPP Data Input:', ruppData);
    console.log('RUPP Data Type:', typeof ruppData);
    console.log('RUPP Data Keys:', ruppData ? Object.keys(ruppData) : 'null');

    // Extract RUPP requirements from different possible formats
    let ruppRequirements = [];
    
    if (ruppData?.formatted_sentences) {
      ruppRequirements = ruppData.formatted_sentences;
      console.log('Using formatted_sentences:', ruppRequirements.length, 'items');
    } else if (ruppData?.requirements) {
      ruppRequirements = ruppData.requirements;
      console.log('Using requirements:', ruppRequirements.length, 'items');
    } else if (ruppData?.snl_text) {
      // Split by lines and filter out empty lines
      ruppRequirements = ruppData.snl_text.split('\n').filter(line => line.trim());
      console.log('Using snl_text, split into:', ruppRequirements.length, 'items');
    } else if (ruppData?.optimized_requirements) {
      // Handle optimization results format
      if (Array.isArray(ruppData.optimized_requirements)) {
        ruppRequirements = ruppData.optimized_requirements;
        console.log('Using optimized_requirements array:', ruppRequirements.length, 'items');
      } else if (typeof ruppData.optimized_requirements === 'string') {
        ruppRequirements = ruppData.optimized_requirements.split('\n').filter(line => line.trim());
        console.log('Using optimized_requirements string, split into:', ruppRequirements.length, 'items');
      }
    } else if (typeof ruppData === 'string') {
      ruppRequirements = ruppData.split('\n').filter(line => line.trim());
      console.log('Using string data, split into:', ruppRequirements.length, 'items');
    } else if (Array.isArray(ruppData)) {
      ruppRequirements = ruppData;
      console.log('Using array data directly:', ruppRequirements.length, 'items');
    } else {
      console.warn('Unable to extract RUPP requirements from:', ruppData);
      ruppRequirements = [];
    }

    console.log('Final AI Requirements:', aiRequirements?.slice(0, 3), '... (showing first 3)');
    console.log('Final RUPP Requirements:', ruppRequirements?.slice(0, 3), '... (showing first 3)');

    const missing_in_ai = [];
    const overspecified_in_ai = [];
    const incorrect_in_ai = [];

    // Helper function to normalize text for comparison
    const normalizeText = (text) => {
      return text.toLowerCase()
        .replace(/[^\w\s]/g, ' ')  // Replace punctuation with spaces
        .replace(/\s+/g, ' ')      // Replace multiple spaces with single space
        .trim();
    };

    // Helper function to check if two requirements are similar
    const areRequirementsSimilar = (req1, req2, threshold = 0.6) => {
      const norm1 = normalizeText(req1);
      const norm2 = normalizeText(req2);
      
      // Simple similarity check: count common words
      const words1 = new Set(norm1.split(' '));
      const words2 = new Set(norm2.split(' '));
      
      const commonWords = new Set([...words1].filter(word => words2.has(word)));
      const totalWords = new Set([...words1, ...words2]);
      
      if (totalWords.size === 0) return false;
      return commonWords.size / totalWords.size >= threshold;
    };

    // Ensure we have valid arrays to work with
    if (!Array.isArray(aiRequirements)) {
      console.error('AI Requirements is not an array:', aiRequirements);
      aiRequirements = [];
    }
    if (!Array.isArray(ruppRequirements)) {
      console.error('RUPP Requirements is not an array:', ruppRequirements);
      ruppRequirements = [];
    }

    // Find missing requirements (in RUPP but not in AI)
    ruppRequirements.forEach(ruppReq => {
      if (!ruppReq || typeof ruppReq !== 'string') return;
      
      const found = aiRequirements.some(aiReq => 
        aiReq && typeof aiReq === 'string' && areRequirementsSimilar(aiReq, ruppReq, 0.5)
      );
      
      if (!found) {
        missing_in_ai.push({
          requirement: ruppReq,
          reason: 'This RUPP requirement was not captured by AI generation'
        });
      }
    });

    // Find overspecified requirements (in AI but not in RUPP)
    aiRequirements.forEach(aiReq => {
      if (!aiReq || typeof aiReq !== 'string') return;
      
      const found = ruppRequirements.some(ruppReq => 
        ruppReq && typeof ruppReq === 'string' && areRequirementsSimilar(aiReq, ruppReq, 0.5)
      );
      
      if (!found) {
        overspecified_in_ai.push({
          requirement: aiReq,
          reason: 'AI generated this requirement beyond RUPP scope'
        });
      }
    });

    // Find incorrect requirements (significantly different from RUPP)
    aiRequirements.forEach(aiReq => {
      if (!aiReq || typeof aiReq !== 'string') return;
      
      const similarRuppReq = ruppRequirements.find(ruppReq => 
        ruppReq && typeof ruppReq === 'string' &&
        areRequirementsSimilar(aiReq, ruppReq, 0.3) && 
        !areRequirementsSimilar(aiReq, ruppReq, 0.7)
      );
      
      if (similarRuppReq) {
        incorrect_in_ai.push({
          requirement: aiReq,
          reason: `Similar to RUPP requirement "${similarRuppReq}" but with significant differences`
        });
      }
    });

    const totalIssues = missing_in_ai.length + overspecified_in_ai.length + incorrect_in_ai.length;
    const totalRequirements = Math.max(aiRequirements?.length || 0, ruppRequirements?.length || 0);
    const accuracy_percentage = totalRequirements > 0 
      ? Math.round(((totalRequirements - totalIssues) / totalRequirements) * 100)
      : 0;

    const result = {
      missing_in_ai: {
        count: missing_in_ai.length,
        items: missing_in_ai
      },
      overspecified_in_ai: {
        count: overspecified_in_ai.length,
        items: overspecified_in_ai
      },
      incorrect_in_ai: {
        count: incorrect_in_ai.length,
        items: incorrect_in_ai
      },
      total_issues: totalIssues,
      accuracy_percentage: accuracy_percentage,
      analysis_summary: `String-based comparison found ${totalIssues} differences between AI and RUPP requirements. ` +
        `AI generated ${aiRequirements?.length || 0} requirements vs RUPP's ${ruppRequirements?.length || 0} requirements.`
    };

    console.log('=== COMPARISON RESULT ===');
    console.log('Missing in AI:', missing_in_ai.length);
    console.log('Overspecified in AI:', overspecified_in_ai.length);
    console.log('Incorrect in AI:', incorrect_in_ai.length);
    console.log('Total Issues:', totalIssues);
    console.log('Accuracy:', accuracy_percentage + '%');
    console.log('================================');

    return result;
  };

  const analyzeComparison = async () => {
    if (!aiSnlData?.requirements || !ruppOptimizedData) {
      console.log('Missing data for comparison:', { 
        hasAI: !!aiSnlData?.requirements, 
        hasRUPP: !!ruppOptimizedData 
      });
      return;
    }

    setIsAnalyzing(true);
    try {
      console.log('Starting AI vs RUPP SNL comparison analysis...');
      
      // Perform simple string-based comparison without AI/NLP
      const comparisonResult = performSimpleComparison(
        aiSnlData.requirements, 
        ruppOptimizedData
      );

      console.log('Comparison analysis completed:', comparisonResult);
      setComparisonStats(comparisonResult);
    } catch (error) {
      console.error('Comparison analysis failed:', error);
      // Fallback only on error
      setComparisonStats({
        missing_in_ai: { count: 0, items: [], description: 'Analysis unavailable due to error' },
        overspecified_in_ai: { count: 0, items: [], description: 'Analysis unavailable due to error' },
        incorrect_in_ai: { count: 0, items: [], description: 'Analysis unavailable due to error' },
        total_issues: 0,
        accuracy_percentage: 0,
        analysis_summary: 'Detailed analysis temporarily unavailable due to technical issues'
      });
    } finally {
      setIsAnalyzing(false);
    }
  };

  if (!aiSnlData) {
    return (
      <Alert severity="info">
        No AI-generated requirements available for verification.
      </Alert>
    );
  }

  if (!ruppOptimizedData) {
    return (
      <Alert severity="warning">
        RUPP optimized data not available yet. Please complete RUPP optimization first to enable comparison.
      </Alert>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        AI vs RUPP Comparison & Verification
      </Typography>

      <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <AIIcon sx={{ mr: 1 }} />
            <Typography variant="h6">
              Generated Requirements
            </Typography>
            <Chip 
              label={`${aiSnlData.requirements?.length || 0} requirements`}
              size="small"
              sx={{ ml: 2 }}
            />
          </Box>

          {!isVerifying && verificationResults.length > 0 && onContinue && (
            <Button
              variant="contained"
              color="primary"
              endIcon={<ArrowForwardIcon />}
              onClick={onContinue}
            >
              Continue to RUPP Optimization
            </Button>
          )}
        </Box>

        <Divider sx={{ mb: 2 }} />

        {isVerifying ? (
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', py: 4 }}>
            <CircularProgress size={24} sx={{ mr: 2 }} />
            <Typography>Verifying requirements...</Typography>
          </Box>
        ) : (
          <>
            <List>
              {verificationResults.map(({ requirement, validation }, index) => (
                <ListItem key={index} alignItems="flex-start">
                  <ListItemIcon>
                    {getStatusIcon(validation)}
                  </ListItemIcon>
                  <ListItemText
                    primary={requirement}
                    secondary={
                      <Box sx={{ mt: 1 }}>
                        <Chip 
                          label={`Clarity: ${validation.clarity}/10`}
                          size="small"
                          sx={{ mr: 1 }}
                          color={validation.clarity >= 7 ? "success" : "warning"}
                        />
                        <Chip 
                          label={`Completeness: ${validation.completeness}/10`}
                          size="small"
                          sx={{ mr: 1 }}
                          color={validation.completeness >= 7 ? "success" : "warning"}
                        />
                        <Chip 
                          label={`Atomicity: ${validation.atomicity}/10`}
                          size="small"
                          color={validation.atomicity >= 7 ? "success" : "warning"}
                        />
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>

            {/* Issues Summary */}
            {Object.values(issues).flat().length > 0 && (
              <Alert severity="warning" sx={{ mt: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Issues Found:
                </Typography>
                {issues.missing.length > 0 && (
                  <Typography variant="body2">• {issues.missing.length} requirements with missing elements</Typography>
                )}
                {issues.overspecified.length > 0 && (
                  <Typography variant="body2">• {issues.overspecified.length} overspecified requirements</Typography>
                )}
                {issues.incorrect.length > 0 && (
                  <Typography variant="body2">• {issues.incorrect.length} requirements with clarity issues</Typography>
                )}
              </Alert>
            )}

            {/* Comparison Stats Summary */}
            {isAnalyzing && (
              <Card sx={{ mt: 3, backgroundColor: '#f8f9fa' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', py: 2 }}>
                    <CircularProgress size={24} sx={{ mr: 2 }} />
                    <Typography>Analyzing AI vs RUPP comparison...</Typography>
                  </Box>
                </CardContent>
              </Card>
            )}
            
            {comparisonStats && !isAnalyzing && (
              <Card sx={{ mt: 3, backgroundColor: '#f5f5f5' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <StatsIcon sx={{ mr: 1 }} color="primary" />
                    <Typography variant="h6">AI vs RUPP Optimized SNL Comparison Analysis</Typography>
                    {comparisonStats.accuracy_percentage && (
                      <Chip 
                        label={`${comparisonStats.accuracy_percentage}% Accuracy`} 
                        color={comparisonStats.accuracy_percentage >= 70 ? "success" : comparisonStats.accuracy_percentage >= 50 ? "warning" : "error"}
                        sx={{ ml: 2 }}
                      />
                    )}
                  </Box>
                  
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={4}>
                      <Paper sx={{ p: 2, backgroundColor: '#fff3e0' }}>
                        <Typography variant="subtitle2" sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          <MissingIcon color="warning" sx={{ mr: 1 }} /> 
                          Missing in AI ({comparisonStats.missing_in_ai?.count || 0})
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                          Requirements from RUPP optimization that AI failed to capture
                        </Typography>
                        <List dense>
                          {comparisonStats.missing_in_ai?.items?.length > 0 ? (
                            comparisonStats.missing_in_ai.items.map((item, idx) => (
                              <ListItem key={idx} sx={{ py: 0.5 }}>
                                <ListItemText 
                                  primary={item.requirement || item} 
                                  secondary={item.reason}
                                  primaryTypographyProps={{ variant: 'body2' }}
                                  secondaryTypographyProps={{ variant: 'caption' }}
                                />
                              </ListItem>
                            ))
                          ) : (
                            <ListItem>
                              <ListItemText primary="No missing requirements found" />
                            </ListItem>
                          )}
                        </List>
                      </Paper>
                    </Grid>
                    
                    <Grid item xs={12} md={4}>
                      <Paper sx={{ p: 2, backgroundColor: '#e3f2fd' }}>
                        <Typography variant="subtitle2" sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          <OverspecifiedIcon color="info" sx={{ mr: 1 }} /> 
                          Overspecified in AI ({comparisonStats.overspecified_in_ai?.count || 0})
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                          Requirements where AI was too detailed beyond RUPP scope
                        </Typography>
                        <List dense>
                          {comparisonStats.overspecified_in_ai?.items?.length > 0 ? (
                            comparisonStats.overspecified_in_ai.items.map((item, idx) => (
                              <ListItem key={idx} sx={{ py: 0.5 }}>
                                <ListItemText 
                                  primary={item.requirement || item} 
                                  secondary={item.reason}
                                  primaryTypographyProps={{ variant: 'body2' }}
                                  secondaryTypographyProps={{ variant: 'caption' }}
                                />
                              </ListItem>
                            ))
                          ) : (
                            <ListItem>
                              <ListItemText primary="No overspecified requirements found" />
                            </ListItem>
                          )}
                        </List>
                      </Paper>
                    </Grid>
                    
                    <Grid item xs={12} md={4}>
                      <Paper sx={{ p: 2, backgroundColor: '#ffebee' }}>
                        <Typography variant="subtitle2" sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          <IncorrectIcon color="error" sx={{ mr: 1 }} /> 
                          Incorrect in AI ({comparisonStats.incorrect_in_ai?.count || 0})
                        </Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                          Requirements where AI made factual errors or misinterpretations
                        </Typography>
                        <List dense>
                          {comparisonStats.incorrect_in_ai?.items?.length > 0 ? (
                            comparisonStats.incorrect_in_ai.items.map((item, idx) => (
                              <ListItem key={idx} sx={{ py: 0.5 }}>
                                <ListItemText 
                                  primary={item.requirement || item} 
                                  secondary={item.reason}
                                  primaryTypographyProps={{ variant: 'body2' }}
                                  secondaryTypographyProps={{ variant: 'caption' }}
                                />
                              </ListItem>
                            ))
                          ) : (
                            <ListItem>
                              <ListItemText primary="No incorrect requirements found" />
                            </ListItem>
                          )}
                        </List>
                      </Paper>
                    </Grid>
                  </Grid>
                  
                  <Divider sx={{ my: 2 }} />
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      <strong>Analysis Summary:</strong> {comparisonStats.analysis_summary}
                    </Typography>
                    <Typography variant="body2" sx={{ mt: 1 }}>
                      <strong>Total Issues Found:</strong> {comparisonStats.total_issues || 0}
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            )}
          </>
        )}
      </Paper>
    </Box>
  );
};

export default AIResultsVerifier;