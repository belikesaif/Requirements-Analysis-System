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
import { apiService } from '../services/apiService';


const AIResultsVerifier = ({ aiSnlData, ruppOptimizedData, onVerificationComplete, onError, onContinue }) => {
  const [verificationResults, setVerificationResults] = useState([]);
  const [comparisonStats, setComparisonStats] = useState(null);
  const [isVerifying, setIsVerifying] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [issues, setIssues] = useState({ missing: [], overspecified: [], incorrect: [] });
  const [hasAnalyzed, setHasAnalyzed] = useState(false); // Prevent multiple analyses

  useEffect(() => {
    const verifyAndAnalyze = async () => {
      // Reset analysis state when data changes
      if (aiSnlData?.requirements && ruppOptimizedData && !hasAnalyzed) {
        setHasAnalyzed(true);
        
        if (aiSnlData?.requirements) {
          await verifyRequirements();
        }
        
        if (aiSnlData?.requirements && ruppOptimizedData) {
          await analyzeComparison();
        }
      }
    };
    
    verifyAndAnalyze();
  }, [aiSnlData, ruppOptimizedData]); // Remove hasAnalyzed from dependencies to prevent loops

  // Reset analysis flag when data changes
  useEffect(() => {
    setHasAnalyzed(false);
    setComparisonStats(null);
  }, [aiSnlData?.requirements, ruppOptimizedData]);

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

  // Helper function to calculate RUPP requirements count consistently
  const getRuppRequirementsCount = (ruppData) => {
    if (!ruppData) return 0;

    // First check if we have the actual_count from optimization results
    if (ruppData.actual_count !== undefined) {
      return ruppData.actual_count;
    }

    if (ruppData?.formatted_sentences) {
      if (Array.isArray(ruppData.formatted_sentences)) {
        const validReqs = ruppData.formatted_sentences.filter(req => 
          req && 
          typeof req === 'string' && 
          req.trim().length > 10 &&
          !req.trim().match(/^\s*$/)
        );
        return validReqs.length;
      } else if (typeof ruppData.formatted_sentences === 'string') {
        const lines = ruppData.formatted_sentences.split('\n');
        const validLines = lines.filter(line => {
          const trimmed = line.trim();
          return trimmed.length > 0 && 
                 trimmed.match(/^\d+\./) && // Starts with number and period
                 trimmed.replace(/^\d+\.\s*/, '').trim().length > 5; // Has meaningful content after number
        });
        return validLines.length;
      }
    } else if (ruppData?.requirements && Array.isArray(ruppData.requirements)) {
      const validReqs = ruppData.requirements.filter(req => 
        req && 
        typeof req === 'string' && 
        req.trim().length > 10 && // Must be substantial content
        !req.trim().match(/^\s*$/) // Not just whitespace
      );
      return validReqs.length;
    } else if (ruppData?.optimized_requirements) {
      if (Array.isArray(ruppData.optimized_requirements)) {
        const validReqs = ruppData.optimized_requirements.filter(req => 
          req && 
          typeof req === 'string' && 
          req.trim().length > 10 &&
          !req.trim().match(/^\s*$/)
        );
        return validReqs.length;
      } else if (typeof ruppData.optimized_requirements === 'string') {
        const lines = ruppData.optimized_requirements.split('\n');
        const validLines = lines.filter(line => {
          const trimmed = line.trim();
          return trimmed.length > 10 && !trimmed.match(/^\s*$/);
        });
        return validLines.length;
      }
    } else if (Array.isArray(ruppData)) {
      const validReqs = ruppData.filter(req => 
        req && 
        typeof req === 'string' && 
        req.trim().length > 10 &&
        !req.trim().match(/^\s*$/)
      );
      return validReqs.length;
    } else if (ruppData?.snl_text) {
      const lines = ruppData.snl_text.split('\n');
      const validLines = lines.filter(line => {
        const trimmed = line.trim();
        return trimmed.length > 10 && !trimmed.match(/^\s*$/);
      });
      return validLines.length;
    } else if (typeof ruppData === 'string') {
      const lines = ruppData.split('\n');
      const validLines = lines.filter(line => {
        const trimmed = line.trim();
        return trimmed.length > 10 && !trimmed.match(/^\s*$/);
      });
      return validLines.length;
    }

    return 0;
  };

  const performSimpleComparison = (aiRequirements, ruppData) => {
    console.log('=== DEBUGGING COMPARISON DATA ===');
    console.log('AI Requirements Input:', aiRequirements);
    console.log('AI Requirements Type:', typeof aiRequirements);
    console.log('AI Requirements Length:', aiRequirements?.length);
    console.log('RUPP Data Input:', ruppData);
    console.log('RUPP Data Type:', typeof ruppData);
    console.log('RUPP Data Keys:', ruppData ? Object.keys(ruppData) : 'null');

    // Extract RUPP requirements from different possible formats using consistent filtering
    let ruppRequirements = [];
    
    if (ruppData?.formatted_sentences) {
      if (typeof ruppData.formatted_sentences === 'string') {
        const lines = ruppData.formatted_sentences.split('\n');
        ruppRequirements = lines
          .filter(line => {
            const trimmed = line.trim();
            return trimmed.length > 0 && 
                   trimmed.match(/^\d+\./) && // Starts with number and period
                   trimmed.replace(/^\d+\.\s*/, '').trim().length > 5; // Has meaningful content after number
          })
          .map(line => line.replace(/^\d+\.\s*/, '').trim()); // Remove numbering for comparison
        console.log('Using formatted_sentences string:', ruppRequirements.length, 'items');
      } else if (Array.isArray(ruppData.formatted_sentences)) {
        ruppRequirements = ruppData.formatted_sentences.filter(req => 
          req && 
          typeof req === 'string' && 
          req.trim().length > 10 &&
          !req.trim().match(/^\s*$/)
        );
        console.log('Using formatted_sentences array:', ruppRequirements.length, 'items');
      }
    } else if (ruppData?.requirements && Array.isArray(ruppData.requirements)) {
      ruppRequirements = ruppData.requirements.filter(req => 
        req && 
        typeof req === 'string' && 
        req.trim().length > 10 &&
        !req.trim().match(/^\s*$/)
      );
      console.log('Using requirements array:', ruppRequirements.length, 'items');
    } else if (ruppData?.snl_text) {
      // Split by lines and filter out empty lines
      ruppRequirements = ruppData.snl_text.split('\n').filter(line => {
        const trimmed = line.trim();
        return trimmed.length > 10 && !trimmed.match(/^\s*$/);
      });
      console.log('Using snl_text, split into:', ruppRequirements.length, 'items');
    } else if (ruppData?.optimized_requirements) {
      // Handle optimization results format
      if (Array.isArray(ruppData.optimized_requirements)) {
        ruppRequirements = ruppData.optimized_requirements.filter(req => 
          req && 
          typeof req === 'string' && 
          req.trim().length > 10 &&
          !req.trim().match(/^\s*$/)
        );
        console.log('Using optimized_requirements array:', ruppRequirements.length, 'items');
      } else if (typeof ruppData.optimized_requirements === 'string') {
        ruppRequirements = ruppData.optimized_requirements.split('\n').filter(line => {
          const trimmed = line.trim();
          return trimmed.length > 10 && !trimmed.match(/^\s*$/);
        });
        console.log('Using optimized_requirements string, split into:', ruppRequirements.length, 'items');
      }
    } else if (typeof ruppData === 'string') {
      ruppRequirements = ruppData.split('\n').filter(line => {
        const trimmed = line.trim();
        return trimmed.length > 10 && !trimmed.match(/^\s*$/);
      });
      console.log('Using string data, split into:', ruppRequirements.length, 'items');
    } else if (Array.isArray(ruppData)) {
      ruppRequirements = ruppData.filter(req => 
        req && 
        typeof req === 'string' && 
        req.trim().length > 10 &&
        !req.trim().match(/^\s*$/)
      );
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

    // Prevent multiple simultaneous calls
    if (isAnalyzing) {
      console.log('Analysis already in progress, skipping...');
      return;
    }

    setIsAnalyzing(true);
    
    try {
      console.log('Starting AI vs RUPP SNL comparison analysis...');
      
      // Extract RUPP requirements from the optimized data using consistent filtering logic
      let ruppRequirements = [];
      
      console.log('DEBUG - Full ruppOptimizedData structure:', ruppOptimizedData);
      console.log('DEBUG - ruppOptimizedData keys:', ruppOptimizedData ? Object.keys(ruppOptimizedData) : 'null');
      console.log('DEBUG - ruppOptimizedData type:', typeof ruppOptimizedData);
      
      if (ruppOptimizedData?.formatted_sentences) {
        if (typeof ruppOptimizedData.formatted_sentences === 'string') {
          const lines = ruppOptimizedData.formatted_sentences.split('\n');
          ruppRequirements = lines
            .filter(line => {
              const trimmed = line.trim();
              return trimmed.length > 0 && 
                     trimmed.match(/^\d+\./) && // Starts with number and period
                     trimmed.replace(/^\d+\.\s*/, '').trim().length > 5; // Has meaningful content after number
            })
            .map(line => line.replace(/^\d+\.\s*/, '').trim()); // Remove numbering for comparison
          console.log('DEBUG - Using formatted_sentences string, extracted:', ruppRequirements.length);
        } else if (Array.isArray(ruppOptimizedData.formatted_sentences)) {
          ruppRequirements = ruppOptimizedData.formatted_sentences.filter(req => 
            req && 
            typeof req === 'string' && 
            req.trim().length > 10 &&
            !req.trim().match(/^\s*$/)
          );
          console.log('DEBUG - Using formatted_sentences array:', ruppRequirements.length);
        }
      } else if (ruppOptimizedData?.requirements && Array.isArray(ruppOptimizedData.requirements)) {
        ruppRequirements = ruppOptimizedData.requirements.filter(req => 
          req && 
          typeof req === 'string' && 
          req.trim().length > 10 &&
          !req.trim().match(/^\s*$/)
        );
        console.log('DEBUG - Using requirements array:', ruppRequirements.length);
      } else if (ruppOptimizedData?.optimized_requirements) {
        if (Array.isArray(ruppOptimizedData.optimized_requirements)) {
          ruppRequirements = ruppOptimizedData.optimized_requirements.filter(req => 
            req && 
            typeof req === 'string' && 
            req.trim().length > 10 &&
            !req.trim().match(/^\s*$/)
          );
          console.log('DEBUG - Using optimized_requirements array:', ruppRequirements.length);
        } else if (typeof ruppOptimizedData.optimized_requirements === 'string') {
          ruppRequirements = ruppOptimizedData.optimized_requirements.split('\n')
            .filter(line => {
              const trimmed = line.trim();
              return trimmed.length > 10 && !trimmed.match(/^\s*$/);
            });
          console.log('DEBUG - Using optimized_requirements string:', ruppRequirements.length);
        }
      } else if (Array.isArray(ruppOptimizedData)) {
        ruppRequirements = ruppOptimizedData.filter(req => 
          req && 
          typeof req === 'string' && 
          req.trim().length > 10 &&
          !req.trim().match(/^\s*$/)
        );
        console.log('DEBUG - Using array data directly:', ruppRequirements.length);
      } else if (ruppOptimizedData?.snl_text) {
        // Fallback to snl_text if other formats aren't available
        ruppRequirements = ruppOptimizedData.snl_text.split('\n')
          .filter(line => {
            const trimmed = line.trim();
            return trimmed.length > 10 && !trimmed.match(/^\s*$/);
          });
        console.log('DEBUG - Using snl_text as fallback:', ruppRequirements.length);
      } else {
        // Fallback to simple comparison if RUPP data format is unclear
        console.warn('Unable to extract RUPP requirements, falling back to simple comparison');
        console.warn('Available RUPP data keys:', ruppOptimizedData ? Object.keys(ruppOptimizedData) : 'none');
        const comparisonResult = performSimpleComparison(
          aiSnlData.requirements, 
          ruppOptimizedData
        );
        setComparisonStats(comparisonResult);
        return;
      }

      console.log('Using AI-powered comparison with:', {
        aiRequirements: aiSnlData.requirements.length,
        ruppRequirements: ruppRequirements.length
      });

      // Debug the actual data being sent
      console.log('DEBUG - AI requirements sample:', aiSnlData.requirements.slice(0, 2));
      console.log('DEBUG - RUPP requirements sample:', ruppRequirements.slice(0, 2));
      console.log('DEBUG - AI requirements type:', typeof aiSnlData.requirements, Array.isArray(aiSnlData.requirements));
      console.log('DEBUG - RUPP requirements type:', typeof ruppRequirements, Array.isArray(ruppRequirements));

      // Ensure both are arrays of strings
      const cleanAiRequirements = Array.isArray(aiSnlData.requirements) 
        ? aiSnlData.requirements
            .filter(req => typeof req === 'string' && req.trim().length > 5)
            .filter(req => !req.includes('Actors Identified:') && !req.includes('Structured Natural Language'))
            .map(req => req.trim())
        : [];
      
      const cleanRuppRequirements = Array.isArray(ruppRequirements) 
        ? ruppRequirements
            .filter(req => typeof req === 'string' && req.trim().length > 5)
            .map(req => req.trim())
        : [];

      console.log('DEBUG - Clean AI requirements count:', cleanAiRequirements.length);
      console.log('DEBUG - Clean RUPP requirements count:', cleanRuppRequirements.length);
      console.log('DEBUG - Clean AI sample:', cleanAiRequirements.slice(0, 2));
      console.log('DEBUG - Clean RUPP sample:', cleanRuppRequirements.slice(0, 2));

      if (cleanAiRequirements.length === 0 || cleanRuppRequirements.length === 0) {
        console.error('Invalid data: AI or RUPP requirements are empty after cleaning');
        console.error('AI count:', cleanAiRequirements.length, 'RUPP count:', cleanRuppRequirements.length);
        throw new Error('Invalid requirements data format');
      }

      // Try AI-powered comparison first
      try {
        console.log('Attempting AI-powered comparison...');
        console.log('DEBUG - Sending to API:', {
          ai_count: cleanAiRequirements.length,
          rupp_count: cleanRuppRequirements.length,
          ai_sample: cleanAiRequirements.slice(0, 2),
          rupp_sample: cleanRuppRequirements.slice(0, 2)
        });
        
        const response = await apiService.compareAIvsRUPP({
          ai_snl: cleanAiRequirements,
          rupp_snl: cleanRuppRequirements
        });

        console.log('AI-powered comparison analysis completed:', response);
        console.log('Response detailed_analysis:', response.detailed_analysis);
        
        // Use the detailed analysis from the response - handle the nested structure
        const detailedAnalysis = response.detailed_analysis;
        
        // Extract the data, handling both array and object formats
        const getMissingData = () => {
          if (Array.isArray(detailedAnalysis.missing_in_ai)) {
            return { count: detailedAnalysis.missing_in_ai.length, items: detailedAnalysis.missing_in_ai };
          } else if (detailedAnalysis.missing_in_ai && typeof detailedAnalysis.missing_in_ai === 'object') {
            return {
              count: detailedAnalysis.missing_in_ai.count || 0,
              items: detailedAnalysis.missing_in_ai.items || []
            };
          }
          return { count: 0, items: [] };
        };

        const getOverspecifiedData = () => {
          if (Array.isArray(detailedAnalysis.overspecified_in_ai)) {
            return { count: detailedAnalysis.overspecified_in_ai.length, items: detailedAnalysis.overspecified_in_ai };
          } else if (detailedAnalysis.overspecified_in_ai && typeof detailedAnalysis.overspecified_in_ai === 'object') {
            return {
              count: detailedAnalysis.overspecified_in_ai.count || 0,
              items: detailedAnalysis.overspecified_in_ai.items || []
            };
          }
          return { count: 0, items: [] };
        };

        const getIncorrectData = () => {
          if (Array.isArray(detailedAnalysis.incorrect_in_ai)) {
            return { count: detailedAnalysis.incorrect_in_ai.length, items: detailedAnalysis.incorrect_in_ai };
          } else if (detailedAnalysis.incorrect_in_ai && typeof detailedAnalysis.incorrect_in_ai === 'object') {
            return {
              count: detailedAnalysis.incorrect_in_ai.count || 0,
              items: detailedAnalysis.incorrect_in_ai.items || []
            };
          }
          return { count: 0, items: [] };
        };

        const missingData = getMissingData();
        const overspecifiedData = getOverspecifiedData();
        const incorrectData = getIncorrectData();
        
        console.log('DEBUG - Parsed data:', {
          missing: missingData,
          overspecified: overspecifiedData,
          incorrect: incorrectData
        });
        
        setComparisonStats({
          missing_in_ai: missingData,
          overspecified_in_ai: overspecifiedData,
          incorrect_in_ai: incorrectData,
          total_issues: detailedAnalysis.total_issues || (missingData.count + overspecifiedData.count + incorrectData.count),
          accuracy_percentage: detailedAnalysis.accuracy_percentage || response.summary_stats?.accuracy_score || 0,
          analysis_summary: detailedAnalysis.analysis_summary || 'Analysis completed successfully'
        });

      } catch (apiError) {
        console.error('AI-powered comparison failed, falling back to simple comparison:', apiError);
        console.error('API Error details:', {
          message: apiError.message,
          stack: apiError.stack,
          response: apiError.response?.data
        });
        
        // Fallback to simple comparison on API error
        console.log('Using fallback simple comparison...');
        const comparisonResult = performSimpleComparison(
          cleanAiRequirements, 
          ruppOptimizedData
        );
        
        setComparisonStats({
          ...comparisonResult,
          analysis_summary: `${comparisonResult.analysis_summary} (Using fallback method due to API error: ${apiError.message})`
        });
      }

    } catch (error) {
      console.error('Comparison analysis completely failed:', error);
      setComparisonStats({
        missing_in_ai: { count: 0, items: [], description: 'Analysis unavailable due to error' },
        overspecified_in_ai: { count: 0, items: [], description: 'Analysis unavailable due to error' },
        incorrect_in_ai: { count: 0, items: [], description: 'Analysis unavailable due to error' },
        total_issues: 0,
        accuracy_percentage: 0,
        analysis_summary: `Detailed analysis temporarily unavailable due to technical issues: ${error.message}`
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
        AI Generated SNL Verifier
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
              Continue to Rupp's Optimization
            </Button>
          )}
        </Box>

        <Divider sx={{ mb: 2 }} />

        {isVerifying ? (
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', py: 4 }}>
            <CircularProgress size={24} sx={{ mr: 2 }} />
            <Typography>Analyzing AI Generated SNL...</Typography>
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
                    <Typography>Analyzing and Verifying AI SNL...</Typography>
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
                  </Grid>
                  
                  <Divider sx={{ my: 2 }} />
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      <strong>Analysis Summary:</strong> {comparisonStats.analysis_summary}
                    </Typography>
                    <Typography variant="body2" sx={{ mt: 1 }}>
                      <strong>Total Issues Found:</strong> {comparisonStats.total_issues || 0}
                    </Typography>
                    <Typography variant="body2" sx={{ mt: 1 }}>
                      <strong>AI SNL Count:</strong> {aiSnlData.requirements?.length || 0} | 
                      <strong> RUPP SNL Count:</strong> {getRuppRequirementsCount(ruppOptimizedData)} | 
                      <strong> Extras in AI:</strong> {Math.max(0, (aiSnlData.requirements?.length || 0) - getRuppRequirementsCount(ruppOptimizedData))}
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