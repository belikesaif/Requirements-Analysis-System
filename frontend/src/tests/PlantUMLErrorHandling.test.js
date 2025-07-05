/**
 * Test file to verify PlantUML error handling enhancements
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import PlantUMLViewer from '../components/PlantUMLViewer';
import { apiService } from '../services/apiService';

// Mock the API service
jest.mock('../services/apiService');

describe('Enhanced PlantUML Error Handling', () => {
  const mockOnError = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('should report syntax validation errors to backend', async () => {
    const invalidPlantUML = `
      @startuml
      class InvalidClass {
        missing closing brace
      @enduml
    `;

    apiService.validatePlantUMLSyntax.mockResolvedValue({
      is_valid: false,
      errors: ['Missing closing brace'],
      warnings: [],
      suggestions: ['Check brace matching']
    });

    apiService.reportPlantUMLError.mockResolvedValue({
      status: 'error_reported'
    });

    render(
      <PlantUMLViewer
        plantUMLCode={invalidPlantUML}
        title="Test Diagram"
        diagramType="class"
        onError={mockOnError}
      />
    );

    await waitFor(() => {
      expect(apiService.validatePlantUMLSyntax).toHaveBeenCalledWith({
        plantuml_code: invalidPlantUML,
        diagram_type: 'class'
      });
    });

    await waitFor(() => {
      expect(apiService.reportPlantUMLError).toHaveBeenCalledWith(
        expect.objectContaining({
          diagram_type: 'class',
          error_type: 'syntax_validation',
          plantuml_code: invalidPlantUML
        })
      );
    });

    expect(mockOnError).toHaveBeenCalledWith(
      expect.stringContaining('PlantUML syntax errors')
    );
  });

  test('should retry with alternative servers on image load failure', async () => {
    const validPlantUML = `
      @startuml
      class TestClass {
        +method(): void
      }
      @enduml
    `;

    apiService.validatePlantUMLSyntax.mockResolvedValue({
      is_valid: true,
      errors: [],
      warnings: [],
      suggestions: []
    });

    render(
      <PlantUMLViewer
        plantUMLCode={validPlantUML}
        title="Test Diagram"
        diagramType="class"
        onError={mockOnError}
      />
    );

    // Simulate image load error
    const image = screen.getByAltText('PlantUML Diagram');
    fireEvent.error(image);

    // Should show retry button
    await waitFor(() => {
      expect(screen.getByText('Retry')).toBeInTheDocument();
    });
  });

  test('should show fallback code view when max retries reached', async () => {
    const validPlantUML = `
      @startuml
      class TestClass {
        +method(): void
      }
      @enduml
    `;

    apiService.validatePlantUMLSyntax.mockResolvedValue({
      is_valid: true,
      errors: [],
      warnings: [],
      suggestions: []
    });

    apiService.reportPlantUMLError.mockResolvedValue({
      status: 'error_reported'
    });

    const { rerender } = render(
      <PlantUMLViewer
        plantUMLCode={validPlantUML}
        title="Test Diagram"
        diagramType="class"
        onError={mockOnError}
      />
    );

    // Simulate multiple image load errors to reach max retries
    for (let i = 0; i < 3; i++) {
      const image = screen.getByAltText('PlantUML Diagram');
      fireEvent.error(image);
      rerender(
        <PlantUMLViewer
          plantUMLCode={validPlantUML}
          title="Test Diagram"
          diagramType="class"
          onError={mockOnError}
        />
      );
    }

    await waitFor(() => {
      expect(screen.getByText('Fallback: PlantUML Code Preview')).toBeInTheDocument();
    });

    expect(apiService.reportPlantUMLError).toHaveBeenCalledWith(
      expect.objectContaining({
        error_type: 'image_load_error'
      })
    );
  });
});
