import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  CircularProgress,
  Collapse,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  BugReport as BugIcon,
  Code as CodeIcon,
  AccountTree as ClassIcon,
  Timeline as SequenceIcon,
  Link as RelationIcon,
  Add as AddIcon,
  AutoFixHigh as FixIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  CheckCircle as SuccessIcon
} from '@mui/icons-material';
import { apiService } from '../services/apiService';

const DiagramRetryControls = ({
  originalRequirements,
  classDiagram,
  sequenceDiagram,
  identifiedActors = [],
  onRetryComplete,
  onError,
  disabled = false
}) => {
  const [isRetrying, setIsRetrying] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedIssueType, setSelectedIssueType] = useState('');
  const [customFeedback, setCustomFeedback] = useState('');
  const [retryCount, setRetryCount] = useState(0);
  const [lastRetryResult, setLastRetryResult] = useState(null);
  const [expanded, setExpanded] = useState(false);

  // Define issue types with detailed descriptions
  const issueTypes = [
    {
      id: 'syntax_class',
      label: 'Class Diagram Syntax Issues',
      icon: <CodeIcon />,
      color: 'error',
      description: 'Fix PlantUML syntax errors in the class diagram (invalid syntax, malformed relationships)',
      examples: ['Invalid class definition', 'Incorrect relationship syntax', 'Missing @startuml/@enduml tags']
    },
    {
      id: 'syntax_sequence',
      label: 'Sequence Diagram Syntax Issues',
      icon: <CodeIcon />,
      color: 'error',
      description: 'Fix PlantUML syntax errors in the sequence diagram (invalid participants, malformed messages)',
      examples: ['Invalid participant definition', 'Incorrect message syntax', 'Malformed activation boxes']
    },
    {
      id: 'syntax_both',
      label: 'Syntax Issues in Both Diagrams',
      icon: <BugIcon />,
      color: 'error',
      description: 'Fix PlantUML syntax errors in both class and sequence diagrams',
      examples: ['Multiple syntax errors', 'Common syntax patterns wrong', 'Overall PlantUML compliance']
    },
    {
      id: 'missing_interactions',
      label: 'Missing Interactions in Sequence',
      icon: <SequenceIcon />,
      color: 'warning',
      description: 'Add missing user interactions and message flows to the sequence diagram',
      examples: ['Missing user workflows', 'Incomplete message chains', 'No system responses']
    },
    {
      id: 'missing_classes',
      label: 'Missing Classes in Class Diagram',
      icon: <ClassIcon />,
      color: 'warning',
      description: 'Add missing classes and entities mentioned in the requirements',
      examples: ['Domain objects not included', 'Important entities missing', 'Incomplete class structure']
    },
    {
      id: 'wrong_relationships',
      label: 'Incorrect Relationships',
      icon: <RelationIcon />,
      color: 'warning',
      description: 'Fix incorrect relationships between classes (associations, dependencies, inheritance)',
      examples: ['Wrong association types', 'Incorrect cardinality', 'Missing dependencies']
    },
    {
      id: 'general_improvement',
      label: 'General Quality Improvement',
      icon: <FixIcon />,
      color: 'info',
      description: 'Comprehensive improvement of both diagrams for better quality and completeness',
      examples: ['Better naming conventions', 'Improved structure', 'Enhanced clarity']
    }
  ];

  const handleQuickRetry = async (issueType) => {
    const issue = issueTypes.find(i => i.id === issueType);
    await performRetry(issueType, issue?.description || '');
  };

  const handleCustomRetry = async () => {
    if (!selectedIssueType) {
      onError?.('Please select an issue type');
      return;
    }
    
    await performRetry(selectedIssueType, customFeedback);
    setDialogOpen(false);
    setCustomFeedback('');
    setSelectedIssueType('');
  };

  const performRetry = async (issueType, feedback) => {
    if (!originalRequirements || (!classDiagram && !sequenceDiagram)) {
      onError?.('Missing required data for retry operation');
      return;
    }

    setIsRetrying(true);
    try {
      const retryData = {
        original_requirements: originalRequirements,
        current_class_diagram: classDiagram || '',
        current_sequence_diagram: sequenceDiagram || '',
        issue_type: issueType,
        specific_feedback: feedback,
        retry_count: retryCount,
        identified_actors: identifiedActors
      };

      console.log('Performing retry with data:', retryData);

      const result = await apiService.retryDiagramGeneration(retryData);
      
      setLastRetryResult(result);
      setRetryCount(prev => prev + 1);
      
      // Call the completion callback with the new diagrams
      onRetryComplete?.({
        classDiagram: result.class_diagram,
        sequenceDiagram: result.sequence_diagram,
        improvements: result.improvements_made,
        issueType: result.issue_type,
        retryCount: result.retry_count
      });

    } catch (error) {
      console.error('Retry failed:', error);
      onError?.(error.message);
    } finally {
      setIsRetrying(false);
    }
  };

  const getIssueIcon = (issueId) => {
    const issue = issueTypes.find(i => i.id === issueId);
    return issue?.icon || <RefreshIcon />;
  };

  const getIssueColor = (issueId) => {
    const issue = issueTypes.find(i => i.id === issueId);
    return issue?.color || 'primary';
  };

  return (
    <Card elevation={2} sx={{ mb: 3 }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <RefreshIcon />
            Diagram Retry Controls
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {retryCount > 0 && (
              <Chip
                size="small"
                label={`${retryCount} ${retryCount === 1 ? 'retry' : 'retries'}`}
                color="info"
                variant="outlined"
              />
            )}
            <IconButton
              size="small"
              onClick={() => setExpanded(!expanded)}
              disabled={disabled}
            >
              {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          </Box>
        </Box>

        {/* Quick Action Buttons */}
        <Grid container spacing={2} sx={{ mb: 2 }}>
          {issueTypes.slice(0, 4).map((issue) => (
            <Grid item xs={12} sm={6} md={3} key={issue.id}>
              <Button
                fullWidth
                variant="outlined"
                size="small"
                color={getIssueColor(issue.id)}
                startIcon={getIssueIcon(issue.id)}
                onClick={() => handleQuickRetry(issue.id)}
                disabled={disabled || isRetrying}
                sx={{ 
                  py: 1.5, 
                  fontSize: '0.75rem',
                  textAlign: 'center',
                  minHeight: '60px'
                }}
              >
                {issue.label}
              </Button>
            </Grid>
          ))}
        </Grid>

        {/* Expandable detailed options */}
        <Collapse in={expanded}>
          <Divider sx={{ my: 2 }} />
          
          {/* More issue types */}
          <Typography variant="subtitle2" sx={{ mb: 2 }}>Additional Options:</Typography>
          <Grid container spacing={2} sx={{ mb: 3 }}>
            {issueTypes.slice(4).map((issue) => (
              <Grid item xs={12} sm={6} key={issue.id}>
                <Button
                  fullWidth
                  variant="outlined"
                  color={getIssueColor(issue.id)}
                  startIcon={getIssueIcon(issue.id)}
                  onClick={() => handleQuickRetry(issue.id)}
                  disabled={disabled || isRetrying}
                  sx={{ py: 1.5 }}
                >
                  {issue.label}
                </Button>
              </Grid>
            ))}
          </Grid>

          {/* Custom retry button */}
          <Box sx={{ textAlign: 'center' }}>
            <Button
              variant="contained"
              color="primary"
              startIcon={<AddIcon />}
              onClick={() => setDialogOpen(true)}
              disabled={disabled || isRetrying}
            >
              Custom Retry with Specific Feedback
            </Button>
          </Box>

          {/* Last retry result */}
          {lastRetryResult && (
            <Alert severity="success" sx={{ mt: 2 }}>
              <Typography variant="subtitle2">Last Retry Result:</Typography>
              <Typography variant="body2">
                Issue Type: {lastRetryResult.issue_type}
              </Typography>
              {lastRetryResult.improvements_made?.length > 0 && (
                <List dense>
                  {lastRetryResult.improvements_made.map((improvement, index) => (
                    <ListItem key={index} sx={{ py: 0 }}>
                      <ListItemIcon sx={{ minWidth: 20 }}>
                        <SuccessIcon fontSize="small" color="success" />
                      </ListItemIcon>
                      <ListItemText 
                        primary={improvement}
                        primaryTypographyProps={{ variant: 'body2' }}
                      />
                    </ListItem>
                  ))}
                </List>
              )}
            </Alert>
          )}
        </Collapse>

        {/* Loading state */}
        {isRetrying && (
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', py: 2 }}>
            <CircularProgress size={24} sx={{ mr: 2 }} />
            <Typography variant="body2" color="textSecondary">
              Retrying diagram generation...
            </Typography>
          </Box>
        )}

        {/* Custom retry dialog */}
        <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
          <DialogTitle>Custom Retry with Specific Feedback</DialogTitle>
          <DialogContent>
            <Box sx={{ mb: 3 }}>
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Issue Type</InputLabel>
                <Select
                  value={selectedIssueType}
                  label="Issue Type"
                  onChange={(e) => setSelectedIssueType(e.target.value)}
                >
                  {issueTypes.map((issue) => (
                    <MenuItem key={issue.id} value={issue.id}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {issue.icon}
                        {issue.label}
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              {selectedIssueType && (
                <Alert severity="info" sx={{ mb: 2 }}>
                  <Typography variant="body2">
                    {issueTypes.find(i => i.id === selectedIssueType)?.description}
                  </Typography>
                  <Typography variant="caption" sx={{ display: 'block', mt: 1, fontWeight: 'bold' }}>
                    Examples:
                  </Typography>
                  <ul style={{ margin: '4px 0', paddingLeft: '20px' }}>
                    {issueTypes.find(i => i.id === selectedIssueType)?.examples?.map((example, index) => (
                      <li key={index}>
                        <Typography variant="caption">{example}</Typography>
                      </li>
                    ))}
                  </ul>
                </Alert>
              )}

              <TextField
                fullWidth
                multiline
                rows={4}
                label="Specific Feedback (Optional)"
                placeholder="Describe the specific issues you're seeing or improvements you'd like..."
                value={customFeedback}
                onChange={(e) => setCustomFeedback(e.target.value)}
                helperText="Provide detailed feedback about what's wrong or what should be improved"
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
            <Button 
              onClick={handleCustomRetry}
              variant="contained"
              disabled={!selectedIssueType || isRetrying}
              startIcon={isRetrying ? <CircularProgress size={16} /> : <RefreshIcon />}
            >
              {isRetrying ? 'Retrying...' : 'Retry Diagrams'}
            </Button>
          </DialogActions>
        </Dialog>
      </CardContent>
    </Card>
  );
};

export default DiagramRetryControls;
