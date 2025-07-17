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
  Accordion,
  AccordionSummary,
  AccordionDetails,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tab,
  Tabs,
  IconButton,
  Tooltip,
  LinearProgress,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import {
  Code as CodeIcon,
  PlayArrow as GenerateIcon,
  CheckCircle as SuccessIcon,
  Storage as ClassIcon,
  Functions as MethodIcon,
  DataObject as AttributeIcon,
  Download as DownloadIcon,
  Visibility as PreviewIcon,
  ContentCopy as CopyIcon,
  Folder as PackageIcon,
  ExpandMore as ExpandMoreIcon,
  Settings as ConfigIcon,
  Memory as RAMIcon,
  Speed as PerformanceIcon,
  Assessment as StatsIcon,
  GetApp as ExportIcon
} from '@mui/icons-material';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { apiService } from '../services/apiService';

// Custom TabPanel component for Material-UI Tabs
function CustomTabPanel({ children, value, index, ...other }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`code-tabpanel-${index}`}
      aria-labelledby={`code-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const CodeGenerator = ({ 
  classDiagram,
  onCodeGenerated,
  onError 
}) => {
  const [loading, setLoading] = useState(false);
  const [generatedCode, setGeneratedCode] = useState(null);
  const [activeStep, setActiveStep] = useState(0);
  const [selectedTab, setSelectedTab] = useState(0);
  const [previewDialog, setPreviewDialog] = useState({ open: false, file: null, content: '' });
  const [projectConfig, setProjectConfig] = useState({
    projectName: 'GeneratedProject',
    packageName: 'com.generated'
  });

  // Auto-generate if class diagram is provided
  useEffect(() => {
    if (classDiagram && !generatedCode && !loading) {
      handleCodeGeneration();
    }
  }, [classDiagram]);

  const handleCodeGeneration = async () => {
    if (!classDiagram) {
      onError('No class diagram provided for code generation');
      return;
    }

    setLoading(true);
    setActiveStep(1);
    
    try {
      console.log('Generating Java code from class diagram...');
      
      const response = await apiService.generateCode({
        class_diagram: classDiagram,
        project_name: projectConfig.projectName,
        package_name: projectConfig.packageName
      });

      setGeneratedCode(response);
      setActiveStep(2);

      // Pass data to parent component
      if (onCodeGenerated) {
        onCodeGenerated(response);
      }

    } catch (error) {
      console.error('Code generation error:', error);
      onError(error.message);
      setActiveStep(0);
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event, newValue) => {
    setSelectedTab(newValue);
  };

  const handlePreviewFile = (fileName, content) => {
    setPreviewDialog({
      open: true,
      file: fileName,
      content: content
    });
  };

  const handleCopyCode = (content) => {
    navigator.clipboard.writeText(content);
    // You could add a snackbar notification here
  };

  const handleDownloadFile = (fileName, content) => {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleDownloadProject = () => {
    if (!generatedCode?.java_files) return;

    // Create a simple text-based project structure for download
    let projectContent = `=== ${projectConfig.projectName} ===\n`;
    projectContent += `Generated on: ${new Date().toISOString()}\n`;
    projectContent += `Package Structure: ${JSON.stringify(generatedCode.package_structure, null, 2)}\n\n`;

    Object.entries(generatedCode.java_files).forEach(([fileName, content]) => {
      projectContent += `\n${'='.repeat(50)}\n`;
      projectContent += `FILE: ${fileName}\n`;
      projectContent += `${'='.repeat(50)}\n`;
      projectContent += content;
      projectContent += '\n';
    });

    const blob = new Blob([projectContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${projectConfig.projectName}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const renderProjectConfiguration = () => (
    <Card elevation={1} sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
          <ConfigIcon sx={{ mr: 1 }} />
          Project Configuration
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Project Name"
              value={projectConfig.projectName}
              onChange={(e) => setProjectConfig({ ...projectConfig, projectName: e.target.value })}
              variant="outlined"
              size="small"
            />
          </Grid>
          <Grid item xs={12} sm={6}>
            <TextField
              fullWidth
              label="Package Name"
              value={projectConfig.packageName}
              onChange={(e) => setProjectConfig({ ...projectConfig, packageName: e.target.value })}
              variant="outlined"
              size="small"
              placeholder="com.example.project"
            />
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );

  const renderGenerationStats = () => {
    if (!generatedCode) return null;

    return (
      <Card elevation={1} sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>Generation Statistics</Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'primary.light', color: 'primary.contrastText' }}>
                <Typography variant="h4">{generatedCode.classes_generated}</Typography>
                <Typography variant="body2">Classes Generated</Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'secondary.light', color: 'secondary.contrastText' }}>
                <Typography variant="h4">{generatedCode.generation_summary?.total_attributes || 0}</Typography>
                <Typography variant="body2">Total Attributes</Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'success.light', color: 'success.contrastText' }}>
                <Typography variant="h4">{generatedCode.generation_summary?.total_methods || 0}</Typography>
                <Typography variant="body2">Total Methods</Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Paper sx={{ p: 2, textAlign: 'center', bgcolor: 'info.light', color: 'info.contrastText' }}>
                <Typography variant="h4">{generatedCode.generation_summary?.estimated_lines_of_code || 0}</Typography>
                <Typography variant="body2">Lines of Code</Typography>
              </Paper>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    );
  };

  const renderGenerationProcess = () => (
    <Card elevation={2} sx={{ mb: 3 }}>
      <CardContent>
        <Typography variant="h6" sx={{ mb: 2 }}>Code Generation Process</Typography>
        <Stepper activeStep={activeStep} orientation="vertical">
          <Step>
            <StepLabel>Ready for Generation</StepLabel>
            <StepContent>
              <Typography variant="body2" color="textSecondary">
                PlantUML class diagram is ready. Will parse classes, attributes, and methods.
              </Typography>
            </StepContent>
          </Step>
          <Step>
            <StepLabel>Parsing & Generating</StepLabel>
            <StepContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                {loading && <CircularProgress size={20} />}
                <Typography variant="body2" color="textSecondary">
                  {loading ? 'Analyzing PlantUML and generating Java classes...' : 'Code generation in progress'}
                </Typography>
              </Box>
            </StepContent>
          </Step>
          <Step>
            <StepLabel>Generation Complete</StepLabel>
            <StepContent>
              <Typography variant="body2" color="textSecondary">
                Java code templates generated successfully with full class structure.
              </Typography>
            </StepContent>
          </Step>
        </Stepper>
      </CardContent>
    </Card>
  );

  const renderPackageStructure = () => {
    if (!generatedCode?.package_structure) return null;

    return (
      <Card elevation={1} sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
            <PackageIcon sx={{ mr: 1 }} />
            Package Structure
          </Typography>
          {Object.entries(generatedCode.package_structure).map(([packageName, classes]) => (
            <Accordion key={packageName} sx={{ mb: 1 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="subtitle1">
                  📁 {packageName} ({classes.length} classes)
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                <List dense>
                  {classes.map((className) => (
                    <ListItem key={className}>
                      <ListItemIcon>
                        <ClassIcon fontSize="small" />
                      </ListItemIcon>
                      <ListItemText 
                        primary={`${className}.java`}
                        secondary={`Class: ${className}`}
                      />
                    </ListItem>
                  ))}
                </List>
              </AccordionDetails>
            </Accordion>
          ))}
        </CardContent>
      </Card>
    );
  };

  const renderCodeFiles = () => {
    if (!generatedCode?.java_files) return null;

    const javaFiles = Object.entries(generatedCode.java_files);

    return (
      <Card elevation={2}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center' }}>
              <CodeIcon sx={{ mr: 1 }} />
              Generated Java Files ({javaFiles.length})
            </Typography>
            <Button
              variant="contained"
              startIcon={<ExportIcon />}
              onClick={handleDownloadProject}
              size="small"
            >
              Download Project
            </Button>
          </Box>

          <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
            <Tabs 
              value={selectedTab} 
              onChange={handleTabChange}
              variant="scrollable"
              scrollButtons="auto"
            >
              {javaFiles.map(([fileName], index) => (
                <Tab 
                  key={fileName}
                  label={fileName}
                  id={`code-tab-${index}`}
                  aria-controls={`code-tabpanel-${index}`}
                />
              ))}
            </Tabs>
          </Box>

          {javaFiles.map(([fileName, content], index) => (
            <CustomTabPanel key={fileName} value={selectedTab} index={index}>
              <Box sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                  <Tooltip title="Preview Full File">
                    <IconButton
                      size="small"
                      onClick={() => handlePreviewFile(fileName, content)}
                    >
                      <PreviewIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Copy Code">
                    <IconButton
                      size="small"
                      onClick={() => handleCopyCode(content)}
                    >
                      <CopyIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Download File">
                    <IconButton
                      size="small"
                      onClick={() => handleDownloadFile(fileName, content)}
                    >
                      <DownloadIcon />
                    </IconButton>
                  </Tooltip>
                </Box>

                <SyntaxHighlighter
                  language="java"
                  style={vscDarkPlus}
                  customStyle={{
                    borderRadius: '8px',
                    maxHeight: '500px',
                    fontSize: '14px'
                  }}
                  showLineNumbers={true}
                >
                  {content}
                </SyntaxHighlighter>
              </Box>
            </CustomTabPanel>
          ))}
        </CardContent>
      </Card>
    );
  };

  return (
    <Box sx={{ p: 3 }}>
      <Card elevation={2} sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <CodeIcon sx={{ mr: 2, color: 'primary.main' }} />
            <Typography variant="h5" component="h2">
              Stage 7: Skeletal Code Generation
            </Typography>
          </Box>
          
          <Typography variant="body1" color="textSecondary" sx={{ mb: 3 }}>
            Generate Java code templates from the optimized PlantUML class diagram. 
            Creates complete class structure with attributes, methods, constructors, and getters/setters.
          </Typography>

          <Alert severity="info" sx={{ mb: 3 }}>
            <Typography variant="body2">
              <strong>Code Generation:</strong> Converts PlantUML class diagram into skeletal Java code with 
              proper class structure, package organization, and basic implementation templates.
              {!classDiagram && (
                <span style={{ color: 'orange', marginLeft: 8 }}>
                  ⚠️ Waiting for class diagram from Final LLM Optimization...
                </span>
              )}
            </Typography>
          </Alert>

          <Button
            variant="contained"
            size="large"
            startIcon={loading ? <CircularProgress size={16} /> : <GenerateIcon />}
            onClick={handleCodeGeneration}
            disabled={loading || !classDiagram}
            sx={{ mb: 2 }}
          >
            {loading ? 'Generating Java Code...' : 'Generate Java Code Templates'}
          </Button>
        </CardContent>
      </Card>

      {/* Project Configuration */}
      {renderProjectConfiguration()}

      {/* Generation Process */}
      {renderGenerationProcess()}

      {/* Generation Statistics */}
      {renderGenerationStats()}

      {/* Package Structure */}
      {renderPackageStructure()}

      {/* Generated Code Files */}
      {renderCodeFiles()}

      {/* Empty State */}
      {!generatedCode && !loading && (
        <Card elevation={1}>
          <CardContent sx={{ textAlign: 'center', py: 8 }}>
            <CodeIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="textSecondary" gutterBottom>
              Ready for Code Generation
            </Typography>
            <Typography variant="body2" color="textSecondary">
              {classDiagram 
                ? 'Click "Generate Java Code Templates" to create skeletal Java classes from your PlantUML diagram.'
                : 'Complete the Final LLM Optimization step to get the class diagram for code generation.'
              }
            </Typography>
          </CardContent>
        </Card>
      )}

      {/* Preview Dialog */}
      <Dialog
        open={previewDialog.open}
        onClose={() => setPreviewDialog({ open: false, file: null, content: '' })}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <CodeIcon />
          {previewDialog.file}
        </DialogTitle>
        <DialogContent>
          <SyntaxHighlighter
            language="java"
            style={vscDarkPlus}
            customStyle={{
              borderRadius: '8px',
              fontSize: '14px'
            }}
            showLineNumbers={true}
          >
            {previewDialog.content}
          </SyntaxHighlighter>
        </DialogContent>
        <DialogActions>
          <Button
            startIcon={<CopyIcon />}
            onClick={() => handleCopyCode(previewDialog.content)}
          >
            Copy
          </Button>
          <Button
            startIcon={<DownloadIcon />}
            onClick={() => handleDownloadFile(previewDialog.file, previewDialog.content)}
          >
            Download
          </Button>
          <Button onClick={() => setPreviewDialog({ open: false, file: null, content: '' })}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CodeGenerator;
