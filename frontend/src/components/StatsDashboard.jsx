import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  LinearProgress
} from '@mui/material';
import {
  Speed as SpeedIcon,
  CheckCircle as AccuracyIcon,
  Timeline as TimelineIcon,
  People as PeopleIcon
} from '@mui/icons-material';

const StatsDashboard = ({ comparisonResults }) => {
  if (!comparisonResults) {
    return (
      <Paper elevation={3} sx={{ p: 3, mt: 2 }}>
        <Typography variant="h6" gutterBottom>
          Performance Dashboard
        </Typography>
        <Typography color="text.secondary">
          No comparison data available. Process requirements to see statistics.
        </Typography>
      </Paper>
    );
  }

  const {
    rupp_metrics = {},
    ai_metrics = {},
    comparison = {},
    metrics = {}
  } = comparisonResults;

  // Fallback values with proper handling
  const ruppProcessingTime = rupp_metrics.processing_time || 0;
  const aiProcessingTime = ai_metrics.processing_time || 0;
  const ruppAccuracy = rupp_metrics.accuracy_score || (metrics.accuracy ? metrics.accuracy * 100 : 0);
  const actorsDetected = rupp_metrics.actors_detected || ai_metrics.actors_detected || 0;
  const ruppRequirements = rupp_metrics.requirements_count || 0;
  const aiRequirements = ai_metrics.requirements_count || 0;

  const statsData = [
    {
      title: 'RUPP Processing Time',
      value: `${ruppProcessingTime.toFixed(1)}ms`,
      icon: <SpeedIcon color="primary" />,
      progress: Math.min((ruppProcessingTime / 1000) * 100, 100)
    },
    {
      title: 'AI Processing Time',
      value: `${aiProcessingTime.toFixed(1)}ms`,
      icon: <TimelineIcon color="secondary" />,
      progress: Math.min((aiProcessingTime / 1000) * 100, 100)
    },
    {
      title: 'RUPP Accuracy',
      value: `${ruppAccuracy.toFixed(1)}%`,
      icon: <AccuracyIcon color="success" />,
      progress: ruppAccuracy
    },
    {
      title: 'Actors Detected',
      value: `${actorsDetected}`,
      icon: <PeopleIcon color="info" />,
      progress: Math.min(actorsDetected * 25, 100)
    }
  ];

  const additionalStats = [
    {
      title: 'RUPP Requirements',
      value: ruppRequirements,
      color: 'primary'
    },
    {
      title: 'AI Requirements', 
      value: aiRequirements,
      color: 'secondary'
    },
    {
      title: 'Precision Score',
      value: `${((metrics.precision || 0) * 100).toFixed(1)}%`,
      color: 'success'
    },
    {
      title: 'Recall Score',
      value: `${((metrics.recall || 0) * 100).toFixed(1)}%`,
      color: 'warning'
    }
  ];

  return (
    <Paper elevation={3} sx={{ p: 3, mt: 2 }}>
      <Typography variant="h6" gutterBottom>
        Performance Dashboard
      </Typography>
        <Grid container spacing={2}>
        {statsData.map((stat, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card elevation={2}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  {stat.icon}
                  <Typography variant="h6" sx={{ ml: 1 }}>
                    {stat.value}
                  </Typography>
                </Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  {stat.title}
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={stat.progress}
                  sx={{ height: 6, borderRadius: 3 }}
                />
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Additional Statistics */}
      <Box sx={{ mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          Detailed Metrics
        </Typography>
        <Grid container spacing={2}>
          {additionalStats.map((stat, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card elevation={1} sx={{ backgroundColor: '#f8f9fa' }}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color={stat.color}>
                    {stat.value}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {stat.title}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>

      {comparison.winner && (
        <Box sx={{ mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            Comparison Summary
          </Typography>
          <Card elevation={1} sx={{ backgroundColor: '#f8f9fa' }}>
            <CardContent>
              <Typography variant="body1">
                <strong>Best Performance:</strong> {comparison.winner}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {comparison.summary || 'Analysis complete'}
              </Typography>
            </CardContent>
          </Card>
        </Box>
      )}
    </Paper>
  );
};

export default StatsDashboard;
