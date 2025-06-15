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
    comparison = {}
  } = comparisonResults;

  const statsData = [
    {
      title: 'RUPP Processing Time',
      value: `${rupp_metrics.processing_time || 0}ms`,
      icon: <SpeedIcon color="primary" />,
      progress: Math.min((rupp_metrics.processing_time || 0) / 1000 * 100, 100)
    },
    {
      title: 'AI Processing Time',
      value: `${ai_metrics.processing_time || 0}ms`,
      icon: <TimelineIcon color="secondary" />,
      progress: Math.min((ai_metrics.processing_time || 0) / 1000 * 100, 100)
    },
    {
      title: 'RUPP Accuracy',
      value: `${rupp_metrics.accuracy_score || 0}%`,
      icon: <AccuracyIcon color="success" />,
      progress: rupp_metrics.accuracy_score || 0
    },
    {
      title: 'Actors Detected',
      value: `${rupp_metrics.actors_detected || 0}`,
      icon: <PeopleIcon color="info" />,
      progress: Math.min((rupp_metrics.actors_detected || 0) * 25, 100)
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
