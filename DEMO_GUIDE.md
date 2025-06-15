# NLP Requirements Analysis System - Demo Guide

## System Overview
This comprehensive NLP Requirements Analysis System compares RUPP (Requirements Understanding and Processing Program) methodology with AI-based approaches for converting natural language requirements into structured SNL (Structured Natural Language).

## Architecture
- **Backend**: FastAPI server with simplified RUPP processor
- **Frontend**: React application with Material-UI components
- **Services**: AI integration, comparison analysis, diagram generation

## Key Features

### 1. Requirements Input
- **Text Input**: Direct requirement text entry
- **File Upload**: Support for .txt and .docx files
- **Preprocessing**: Automatic text cleaning and normalization

### 2. RUPP Processing
- **Actor Identification**: Automatic extraction of system actors
- **Template Matching**: Pattern-based SNL generation
- **Structured Output**: Formatted SNL requirements

### 3. AI Integration
- **Mock AI Service**: Simulated AI-based requirement processing
- **Comparison Analysis**: Side-by-side RUPP vs AI results
- **Performance Metrics**: Accuracy and processing time comparison

### 4. Visualization
- **Results Dashboard**: Interactive comparison interface
- **Diagram Generation**: PlantUML integration for system diagrams
- **Charts**: Performance metrics visualization

## Demo Instructions

### Step 1: Access the Application
1. Open browser to http://localhost:3000 (React frontend)
2. Access API documentation at http://localhost:8000/docs (FastAPI backend)

### Step 2: Input Requirements
1. Use the "Requirements Input" section
2. Either:
   - Type requirements directly in the text area
   - Upload a requirements file (.txt or .docx)

### Step 3: Process Requirements
1. Click "Process with RUPP" to run RUPP analysis
2. Click "Process with AI" to run AI analysis
3. Click "Compare Both" to run comparative analysis

### Step 4: View Results
1. Review SNL output from both approaches
2. Compare accuracy metrics
3. View processing time differences
4. Generate system diagrams if needed

## Sample Test Files
- `sample_requirements.txt`: Basic library management system
- `comprehensive_test_requirements.txt`: Complex e-commerce platform

## Technical Details

### Backend Endpoints
- `POST /api/requirements/process`: Process requirements with RUPP
- `POST /api/requirements/ai-process`: Process with AI (mock)
- `POST /api/requirements/compare`: Compare both approaches
- `GET /api/requirements/{id}`: Retrieve processed requirements
- `POST /api/diagrams/generate`: Generate PlantUML diagrams

### Frontend Components
- `RequirementsInput.jsx`: Input interface
- `SNLComparison.jsx`: Results comparison view
- `App.js`: Main application component

### RUPP Processing Features
- Text preprocessing and cleaning
- Actor identification using regex patterns
- Template-based SNL generation
- Structured output formatting

### Mock AI Features
- Simulated natural language processing
- Template-based response generation
- Configurable processing delays
- Comparison metrics generation

## Performance Metrics
- **Processing Time**: RUPP vs AI comparison
- **Accuracy Score**: Template matching success rate
- **Coverage**: Percentage of requirements processed
- **Actor Detection**: Number of system actors identified

## Future Enhancements
- Real OpenAI integration
- Advanced NLP libraries (spaCy, NLTK)
- Machine learning model training
- Enhanced diagram generation
- Database persistence
- User authentication
- Export functionality
