"""
Main FastAPI application for NLP Requirements Analysis System
"""

from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
from datetime import datetime
from dotenv import load_dotenv

from app.services.nlp_service import NLPService
from app.services.ai_service import AIService
from app.services.comparison_service import ComparisonService
from app.services.diagram_service import DiagramService
from app.storage.memory_storage import MemoryStorage

# Load environment variables
load_dotenv()

app = FastAPI(
    title="NLP Requirements Analysis System",
    description="A system for processing natural language requirements and generating structured SNL with UML diagrams",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React/Vite dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
nlp_service = NLPService()
ai_service = AIService()
comparison_service = ComparisonService()
diagram_service = DiagramService()
storage = MemoryStorage()

# Pydantic models
class CaseStudyRequest(BaseModel):
    text: str
    title: Optional[str] = "Untitled Case Study"

class AIAnalysisRequest(BaseModel):
    ai_snl: List[str]
    original_text: str

class ComparisonRequest(BaseModel):
    rupp_snl: List[str]
    ai_snl: List[str]
    original_text: str

class SNLResponse(BaseModel):
    rupp_snl: Dict[str, Any]
    ai_snl: Dict[str, Any]
    comparison: Dict[str, Any]
    id: str
    timestamp: str
    title: str
    original_text: str

class DiagramGenerationRequest(BaseModel):
    snl_data: Dict[str, Any]
    rupp_snl_text: str

class ActorIdentificationRequest(BaseModel):
    original_requirements: str
    class_diagram: str
    sequence_diagram: str

class FinalOptimizationRequest(BaseModel):
    original_requirements: str
    class_diagram: str
    sequence_diagram: str
    identified_actors: List[str]
    verification_issues: Dict[str, Any]
    diagram_errors: Optional[Dict[str, str]] = None  # Include diagram rendering errors

class RequirementRequest(BaseModel):
    requirement: str

class DiagramVerificationRequest(BaseModel):
    diagram_code: str
    snl_data: Dict[str, Any]
    diagram_type: str

class DiagramOptimizationRequest(BaseModel):
    diagram_code: str
    verification_results: Dict[str, Any]
    diagram_type: str

class PlantUMLErrorReport(BaseModel):
    diagram_type: str
    error_type: str
    error_message: str
    plantuml_code: str
    retry_count: int
    timestamp: str
    validation_status: Optional[Dict[str, Any]] = None

class PlantUMLValidationRequest(BaseModel):
    plantuml_code: str
    diagram_type: str

@app.get("/api/health")
async def health_check():
    """Enhanced health check with PlantUML error handling status"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "features": {
            "plantuml_error_reporting": True,
            "plantuml_validation": True,
            "diagram_error_tracking": True
        },
        "endpoints": [
            "/api/report-plantuml-error",
            "/api/validate-plantuml", 
            "/api/plantuml-error-stats",
            "/api/final-optimization"
        ]
    }

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "NLP Requirements Analysis System API", "status": "active"}

@app.post("/api/process-requirements", response_model=SNLResponse)
async def process_requirements(request: CaseStudyRequest):
    """
    Process case study text and generate both RUPP and AI-based SNL
    """
    try:
        import time
        
        # Generate RUPP SNL with timing
        rupp_start = time.time()
        rupp_result = nlp_service.generate_rupp_snl(request.text)
        rupp_time = (time.time() - rupp_start) * 1000  # Convert to milliseconds
        
        # Add timing information to RUPP result
        rupp_result['processing_time'] = round(rupp_time, 2)
        
        # Generate AI SNL with timing
        ai_start = time.time()
        ai_result = await ai_service.generate_ai_snl(request.text)
        ai_time = (time.time() - ai_start) * 1000  # Convert to milliseconds
        
        # Add timing information to AI result
        ai_result['processing_time'] = round(ai_time, 2)
        
        # Compare results with enhanced AI analysis (AI vs Original Case Study)
        comparison_result = await comparison_service.analyze_ai_snl_detailed(
            ai_result['snl_text'], 
            request.text,
            ai_service
        )        # Store results
        result_id = storage.store_case_study({
            'title': request.title,
            'original_text': request.text,
            'rupp_result': rupp_result,
            'ai_result': ai_result,
            'comparison': comparison_result
        })
        
        # Get the stored case study to retrieve the timestamp
        stored_case_study = storage.get_case_study(result_id)
        
        return SNLResponse(
            rupp_snl=rupp_result,
            ai_snl=ai_result,
            comparison=comparison_result,
            id=result_id,
            timestamp=stored_case_study['timestamp'],
            title=request.title,
            original_text=request.text
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.post("/api/generate-diagrams")
async def generate_diagrams(request: DiagramGenerationRequest):
    """
    Generate PlantUML diagrams from SNL data (Legacy endpoint - kept for compatibility)
    """
    try:
        if hasattr(request, 'diagram_type'):
            # Legacy support
            if request.diagram_type == "class":
                diagram_code = await diagram_service.generate_class_diagram(request.snl_data)
            elif request.diagram_type == "sequence":
                diagram_code = await diagram_service.generate_sequence_diagram(request.snl_data)
            else:
                raise HTTPException(status_code=400, detail="Invalid diagram type. Use 'class' or 'sequence'")
            
            return {
                "diagram_code": diagram_code,
                "diagram_type": request.diagram_type,
                "generated_at": storage.get_current_timestamp(),
                "success": True
            }
        else:
            # New flow - generate both diagrams
            class_diagram = await diagram_service.generate_class_diagram_from_rupp(request.rupp_snl_text)
            sequence_diagram = await diagram_service.generate_sequence_diagram_from_rupp(request.rupp_snl_text)
            
            return {
                "class_diagram": class_diagram,
                "sequence_diagram": sequence_diagram,
                "generated_at": storage.get_current_timestamp(),
                "success": True
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Diagram generation failed: {str(e)}")

@app.post("/api/generate-both-diagrams")
async def generate_both_diagrams(request: DiagramGenerationRequest):
    """
    Generate BOTH class and sequence diagrams simultaneously using RUPP SNL and GPT-3.5
    """
    try:
        print(f"Generating both diagrams with RUPP SNL: {request.rupp_snl_text[:100]}...")
        
        # Generate both diagrams simultaneously using GPT-3.5
        class_diagram = await diagram_service.generate_class_diagram_from_rupp(request.rupp_snl_text)
        sequence_diagram = await diagram_service.generate_sequence_diagram_from_rupp(request.rupp_snl_text)
        
        return {
            "class_diagram": class_diagram,
            "sequence_diagram": sequence_diagram,
            "generation_method": "gpt-3.5-turbo",
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
        
    except Exception as e:
        print(f"Error generating diagrams: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Diagram generation failed: {str(e)}")

@app.post("/api/identify-actors")
async def identify_actors(request: ActorIdentificationRequest):
    """
    Identify actors from original requirements and verify against generated diagrams (Screen 5)
    """
    try:
        print("Identifying actors from requirements and diagrams...")
        
        # Extract actors using POS tagging and NER
        identified_actors = await diagram_service.extract_actors_from_requirements(
            request.original_requirements,
            request.class_diagram,
            request.sequence_diagram
        )
        
        # Verify diagrams against identified actors
        verification_results = await diagram_service.verify_diagrams_with_actors(
            request.class_diagram,
            request.sequence_diagram,
            identified_actors
        )
        
        return {
            "identified_actors": identified_actors,
            "verification_results": verification_results,
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
        
    except Exception as e:
        print(f"Error identifying actors: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Actor identification failed: {str(e)}")

@app.post("/api/final-optimization")
async def final_optimization(request: FinalOptimizationRequest):
    """
    Final LLM optimization using GPT-3.5 with identified actors and verification feedback (Screen 6)
    """
    try:
        print("Performing final LLM optimization with actors...")
        print(f"Request data: {request}")
        
        # Send everything to GPT-3.5 for final optimization
        optimized_diagrams = await diagram_service.optimize_diagrams_with_llm_and_actors(
            original_requirements=request.original_requirements,
            class_diagram=request.class_diagram,
            sequence_diagram=request.sequence_diagram,
            identified_actors=request.identified_actors,
            verification_issues=request.verification_issues,
        )
        
        return {
            "optimized_class_diagram": optimized_diagrams["class_diagram"],
            "optimized_sequence_diagram": optimized_diagrams["sequence_diagram"],
            "improvements": optimized_diagrams["improvements"],
            "final_actors": optimized_diagrams["final_actors"],
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
        
    except Exception as e:
        print(f"Error in final optimization: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Final optimization failed: {str(e)}")

@app.get("/api/comparison-stats")
async def get_comparison_stats():
    """
    Get comparison statistics for research analysis
    """
    try:
        stats = storage.get_comparison_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get comparison stats: {str(e)}")

@app.get("/api/case-studies")
async def get_case_studies():
    """
    Get all stored case studies
    """
    try:
        case_studies = storage.get_all_case_studies()
        return {"case_studies": case_studies}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get case studies: {str(e)}")

@app.get("/api/case-studies/{case_study_id}")
async def get_case_study(case_study_id: str):
    """
    Get specific case study by ID
    """
    try:
        case_study = storage.get_case_study(case_study_id)
        if not case_study:
            raise HTTPException(status_code=404, detail="Case study not found")
        return case_study
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get case study: {str(e)}")

@app.post("/api/upload-file")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and process document files
    """
    try:
        content = await nlp_service.extract_text_from_file(file)
        return {"content": content, "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

@app.get("/api/export-data")
async def export_research_data():
    """
    Export all research data for analysis
    """
    try:
        data = storage.export_all_data()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@app.delete("/api/clear-data")
async def clear_all_data():
    """
    Clear all stored data (for research purposes)
    """
    try:
        storage.clear_all_data()
        return {"message": "All data cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clear operation failed: {str(e)}")

@app.post("/api/validate-requirement")
async def validate_requirement(request: RequirementRequest):
    """
    Validate a single requirement using AI service
    """
    try:
        validation_result = await ai_service.validate_requirement(request.requirement)
        return validation_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

@app.post("/api/verify-diagram")
async def verify_diagram(request: DiagramVerificationRequest):
    """
    Verify a generated diagram against SNL requirements
    """
    try:
        # Verify diagram without access to actors
        verification_result = await diagram_service.verify_diagram(
            request.diagram_code,
            request.snl_data,
            request.diagram_type
        )
        return verification_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Diagram verification failed: {str(e)}")

@app.post("/api/optimize-diagram")
async def optimize_diagram(request: DiagramOptimizationRequest):
    """
    Optimize a diagram based on verification results
    """
    try:
        optimized_result = await diagram_service.optimize_diagram(
            request.diagram_code,
            request.verification_results,
            request.diagram_type
        )
        return optimized_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Diagram optimization failed: {str(e)}")

@app.post("/api/report-plantuml-error")
async def report_plantuml_error(request: PlantUMLErrorReport):
    """
    Report PlantUML rendering error for analysis
    """
    try:
        error_id = storage.store_plantuml_error({
            "diagram_type": request.diagram_type,
            "error_type": request.error_type,
            "error_message": request.error_message,
            "plantuml_code": request.plantuml_code,
            "retry_count": request.retry_count,
            "timestamp": request.timestamp,
            "validation_status": request.validation_status
        })
        
        return {
            "status": "error_reported",
            "error_id": error_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        # Don't fail the request if error reporting fails
        print(f"Warning: Failed to store PlantUML error: {str(e)}")
        return {
            "status": "error_reporting_failed",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/api/validate-plantuml")
async def validate_plantuml(request: PlantUMLValidationRequest):
    """
    Validate PlantUML syntax before rendering
    """
    try:
        validation_result = await diagram_service.validate_plantuml_syntax(
            request.plantuml_code,
            request.diagram_type
        )
        
        validation_result["timestamp"] = datetime.now().isoformat()
        return validation_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PlantUML validation failed: {str(e)}")

@app.get("/api/plantuml-error-stats")
async def get_plantuml_error_stats():
    """
    Get PlantUML error statistics for analysis
    """
    try:
        stats = storage.get_plantuml_error_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get PlantUML error statistics: {str(e)}")

@app.post("/api/analyze-ai-snl-detailed")
async def analyze_ai_snl_detailed(request: AIAnalysisRequest):
    """
    Get detailed analysis of AI SNL vs Original Case Study with Missing, Overspecified, and Incorrect categorization
    """
    try:
        detailed_analysis = await comparison_service.analyze_ai_snl_detailed(
            request.ai_snl, 
            request.original_text,
            ai_service
        )
        
        return {
            "detailed_analysis": detailed_analysis.get('detailed_ai_analysis', {}),
            "summary_stats": {
                "total_ai_requirements": len(detailed_analysis.get('ai_requirements', [])),
                "accuracy_score": detailed_analysis.get('detailed_ai_analysis', {}).get('accuracy_percentage', 0),
                "issues_found": detailed_analysis.get('detailed_ai_analysis', {}).get('total_issues', 0)
            },
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detailed AI SNL analysis failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
