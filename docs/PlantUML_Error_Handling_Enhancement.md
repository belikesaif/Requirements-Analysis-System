# Enhanced PlantUML Error Handling and Backend Communication

## Overview

This enhancement adds comprehensive error detection, reporting, and fallback mechanisms for PlantUML diagram rendering issues in the NLP Requirements System.

## Features Added

### 1. Frontend Enhancements (PlantUMLViewer)

- **Syntax Validation**: Pre-validates PlantUML code before rendering
- **Retry Mechanism**: Automatically retries with alternative servers on failure
- **Error Reporting**: Reports all errors to backend for analysis
- **Fallback Display**: Shows code preview when image rendering fails
- **Visual Indicators**: Displays validation status and retry count

### 2. Backend Enhancements

- **Error Collection**: `/api/report-plantuml-error` endpoint for error reporting
- **Syntax Validation**: `/api/validate-plantuml` endpoint for pre-validation
- **Auto-fixing**: Attempts to fix common syntax issues using AI
- **Error Analytics**: Stores and analyzes error patterns

### 3. Enhanced Communication

- **Bidirectional Error Reporting**: Frontend reports errors to backend
- **Context-Aware Fixes**: Backend provides fixes based on error context
- **Statistics Tracking**: Collects error patterns for system improvement

## Usage Examples

### Basic Usage with Error Handling

```jsx
import PlantUMLViewer from './components/PlantUMLViewer';

function MyComponent() {
  const handleDiagramError = (errorMessage) => {
    console.error('Diagram error:', errorMessage);
    // Handle error (show notification, log, etc.)
  };

  return (
    <PlantUMLViewer
      plantUMLCode={myPlantUMLCode}
      title="My Diagram"
      diagramType="class"
      onError={handleDiagramError}
      showCodeToggle={true}
    />
  );
}
```

### In FinalLLMOptimizer Component

```jsx
// Enhanced error tracking
const [diagramErrors, setDiagramErrors] = useState({
  class: null,
  sequence: null
});

const handleDiagramError = (diagramType, errorMessage) => {
  setDiagramErrors(prev => ({
    ...prev,
    [diagramType]: errorMessage
  }));
};

// Pass errors to optimization
const optimizationData = {
  original_requirements: originalRequirements,
  class_diagram: classDiagram,
  sequence_diagram: sequenceDiagram,
  identified_actors: identifiedActors,
  verification_issues: verificationIssues,
  diagram_errors: diagramErrors // Include rendering errors
};
```

## Error Types Tracked

1. **Syntax Validation Errors**
   - Missing @startuml/@enduml tags
   - Unmatched braces/brackets
   - Invalid PlantUML syntax

2. **Image Load Errors**
   - Server unavailability
   - Network timeouts
   - Invalid diagram encoding

3. **Generation Errors**
   - AI model failures
   - Processing timeouts
   - Invalid responses

## Fallback Mechanisms

### 1. Server Fallback
- Primary: `https://www.plantuml.com/plantuml/svg`
- Secondary: `https://plantuml-server.kkeisuke.dev/svg`
- Tertiary: `http://www.plantuml.com/plantuml/png`

### 2. Display Fallback
- Show PlantUML code as text when image fails
- Provide retry buttons for user intervention
- Display clear error messages with suggestions

### 3. Optimization Fallback
- Include error context in AI optimization requests
- Generate syntax fixes using GPT-3.5
- Maintain fallback content for critical failures

## API Endpoints

### Report PlantUML Error
```
POST /api/report-plantuml-error
{
  "diagram_type": "class",
  "error_type": "syntax_validation",
  "error_message": "Missing @startuml tag",
  "plantuml_code": "class Test { }",
  "retry_count": 1,
  "timestamp": "2025-07-05T10:30:00Z",
  "validation_status": {
    "is_valid": false,
    "errors": ["Missing @startuml tag"]
  }
}
```

### Validate PlantUML Syntax
```
POST /api/validate-plantuml
{
  "plantuml_code": "@startuml\nclass Test { }\n@enduml",
  "diagram_type": "class"
}

Response:
{
  "is_valid": true,
  "errors": [],
  "warnings": [],
  "suggestions": [],
  "timestamp": "2025-07-05T10:30:00Z"
}
```

## Benefits

1. **Improved Reliability**: Proactive error detection and handling
2. **Better User Experience**: Clear error messages and fallback options
3. **System Intelligence**: Error pattern analysis for continuous improvement
4. **Debugging Support**: Comprehensive error logging and reporting
5. **Reduced Downtime**: Multiple fallback mechanisms ensure availability

## Error Analysis Dashboard (Future Enhancement)

The backend collects error statistics that could be used to build an admin dashboard showing:

- Most common error types
- Diagram types with highest failure rates
- Server reliability metrics
- User impact analysis
- Suggested system improvements

## Testing

Run the error handling tests:

```bash
cd frontend
npm test -- PlantUMLErrorHandling.test.js
```

## Configuration

Environment variables for error handling:

```env
# Maximum retry attempts for PlantUML rendering
PLANTUML_MAX_RETRIES=3

# Alternative PlantUML servers (comma-separated)
PLANTUML_FALLBACK_SERVERS=https://plantuml-server.kkeisuke.dev,http://www.plantuml.com

# Enable error reporting to backend
ENABLE_ERROR_REPORTING=true

# Error reporting timeout (ms)
ERROR_REPORTING_TIMEOUT=5000
```

This enhancement significantly improves the system's robustness and provides valuable insights for ongoing system optimization.

## Troubleshooting

### Common Issues and Solutions

#### 1. "Final optimization failed: 422: [object Object]"

**Cause**: Backend validation error or missing required fields.

**Solutions**:
```bash
# Check backend logs for detailed error information
cd backend
python main.py

# Test the health endpoint
curl http://localhost:8000/api/health

# Test final optimization with minimal data
curl -X POST http://localhost:8000/api/final-optimization \
  -H "Content-Type: application/json" \
  -d '{
    "original_requirements": "Test requirement",
    "class_diagram": "@startuml\nclass Test\n@enduml",
    "sequence_diagram": "@startuml\nTest -> Test2\n@enduml", 
    "identified_actors": ["Test"],
    "verification_issues": {}
  }'
```

**Frontend Fix**:
- Ensure all required fields are provided
- Check that `diagram_errors` is only sent when it contains actual errors
- Verify data types match backend expectations

#### 2. PlantUML Images Not Loading

**Symptoms**: Blank diagram areas or constant loading

**Solutions**:
```javascript
// Check browser console for network errors
// Test PlantUML servers manually:
// 1. https://www.plantuml.com/plantuml/svg/
// 2. https://plantuml-server.kkeisuke.dev/svg/
// 3. http://www.plantuml.com/plantuml/png/
