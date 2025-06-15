"""
Main FastAPI application for NLP Requirements Analysis System
"""

from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
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

class ComparisonRequest(BaseModel):
    rupp_snl: List[str]
    ai_snl: List[str]
    original_text: str

class SNLResponse(BaseModel):
    rupp_snl: Dict[str, Any]
    ai_snl: Dict[str, Any]
    comparison: Dict[str, Any]
    id: str

class DiagramRequest(BaseModel):
    snl_data: Dict[str, Any]
    diagram_type: str  # "class" or "sequence"

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
        # Generate RUPP SNL
        rupp_result = nlp_service.generate_rupp_snl(request.text)
        
        # Generate AI SNL
        ai_result = await ai_service.generate_ai_snl(request.text)
        
        # Compare results
        comparison_result = comparison_service.compare_snl(
            rupp_result['snl_text'], 
            ai_result['snl_text'], 
            request.text
        )
        
        # Store results
        result_id = storage.store_case_study({
            'title': request.title,
            'original_text': request.text,
            'rupp_result': rupp_result,
            'ai_result': ai_result,
            'comparison': comparison_result
        })
        
        return SNLResponse(
            rupp_snl=rupp_result,
            ai_snl=ai_result,
            comparison=comparison_result,
            id=result_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.post("/api/generate-diagrams")
async def generate_diagrams(request: DiagramRequest):
    """
    Generate UML diagrams from SNL data using OpenAI
    """
    try:
        if request.diagram_type == "class":
            diagram_code = await diagram_service.generate_class_diagram(request.snl_data)
        elif request.diagram_type == "sequence":
            diagram_code = await diagram_service.generate_sequence_diagram(request.snl_data)
        else:
            raise HTTPException(status_code=400, detail="Invalid diagram type")
        
        # Store diagram data
        diagram_id = storage.store_diagram({
            'type': request.diagram_type,
            'plantuml_code': diagram_code,
            'snl_data': request.snl_data
        })
        
        return {
            'diagram_code': diagram_code,
            'diagram_id': diagram_id,
            'type': request.diagram_type
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Diagram generation failed: {str(e)}")

@app.get("/api/comparison-stats")
async def get_comparison_stats():
    """
    Get verification statistics from stored comparisons
    """
    try:
        stats = storage.get_comparison_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
