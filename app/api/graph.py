"""
Graph execution endpoints
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, BackgroundTasks, Request
from typing import Optional
import os
import tempfile

from fastapi.responses import FileResponse
from app.services.graph_dependencies import get_graph_service 
from app.services.graph_service import GraphService

from app.api.models.schemas import (
    GraphStartResponse, 
    GraphStatusResponse, 
    HITLFeedbackRequest,
    HITLFeedbackResponse,
    ErrorResponse
)
from app.services.graph_service import GraphService
from app.graph.utils.file_preprocessing import CVPreprocessor, CVPreprocessingError
from app.auth.utils import get_current_user
from app.auth.database import get_user_database

router = APIRouter()
preprocessor = CVPreprocessor()


@router.post("/start", 
             response_model=GraphStartResponse, 
             responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}})
async def start_graph(
    request: Request,
    graph_service: GraphService = Depends(get_graph_service),
    cv_file: UploadFile = File(..., description="CV file (docx/pdf)"),
    job_offer: Optional[str] = Form(None, description="Job offer URL or description"),
    current_user = Depends(get_current_user)
):
    """
    Start CV processing graph
    
    Either job_name or job_offer must be provided.
    """
    if not job_offer:
        raise HTTPException(
            status_code=400, 
            detail="Either job_name or job_offer must be provided"
        )
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(cv_file.filename)[1]) as tmp_file:
            content = await cv_file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Preprocess CV
        cv_text = preprocessor.process(tmp_path)
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        # Start graph execution
        thread_id = await graph_service.start_graph(
            cv_text=cv_text,
            job_offer=job_offer,
            request=request,
            current_user=current_user
        )
        
        # Get updated credits after deduction
        from app.auth.database import get_user_database
        user_db = get_user_database(request)
        updated_user = await user_db.increment_credits(current_user.id, 0)  # Get current value
        new_credits = updated_user.credits if updated_user else credits - 20

        return GraphStartResponse(
            thread_id=thread_id,
            status="started",
            message="Graph execution started successfully",
            credits=new_credits
        )
        
    except CVPreprocessingError as e:
        raise HTTPException(status_code=400, detail=f"CV processing error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.get("/status/{thread_id}", response_model=GraphStatusResponse, responses={404: {"model": ErrorResponse}})
async def get_status(thread_id: str, graph_service: GraphService = Depends(get_graph_service) ):
    """
    Get current graph execution status
    
    Returns status, next node, and HITL data if waiting for human input.
    """
    try:
        status = await graph_service.get_status(thread_id)
        return GraphStatusResponse(**status)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.post("/hitl/{thread_id}", response_model=HITLFeedbackResponse, responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}})
async def submit_hitl_feedback(
    thread_id: str,
    feedback: HITLFeedbackRequest,
    graph_service: GraphService = Depends(get_graph_service),
):
    """
    Submit HITL feedback and resume graph execution
    
    Depending on hitl_type:
    - additional_info: provide additional_info field
    - acceptation: provide accepted_cv_data field
    """
    try:
        # Validate feedback based on type
        if feedback.hitl_type == "additional_info" and not feedback.additional_info:
            raise HTTPException(
                status_code=400,
                detail="additional_info field is required for this HITL type"
            )
        
        if feedback.hitl_type == "acceptation" and not feedback.accepted_cv_data:
            raise HTTPException(
                status_code=400,
                detail="accepted_cv_data field is required for this HITL type"
            )
        
        # Submit feedback
        await graph_service.handle_hitl_feedback(
            thread_id, 
            feedback.model_dump(exclude_none=True)
        )
        
        return HITLFeedbackResponse(
            thread_id=thread_id,
            status="resumed",
            message="Graph resumed successfully with provided feedback",
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing feedback: {str(e)}")

def delete_file(path: str):
    try:
        os.remove(path)
    except FileNotFoundError:
        pass

@router.get("/download/{file_id}")
async def download_file(
    file_id: str,
    background_tasks: BackgroundTasks
    ):
    file_path = f"temp_files/{file_id}.pdf"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    background_tasks.add_task(delete_file, file_path)
    
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename="CV.pdf",
        headers={
            "Content-Disposition": "attachment; filename=CV.pdf"
        }
    )

@router.delete("/{thread_id}")
async def cancel_graph(thread_id: str, graph_service: GraphService = Depends(get_graph_service) ):
    """
    Cancel graph execution (optional - for future implementation)
    """
    raise HTTPException(status_code=501, detail="Not implemented yet")

@router.get("/debug/{thread_id}")
async def debug_thread(
    thread_id: str,
    graph_service: GraphService = Depends(get_graph_service)
):
    return {
        "in_memory": thread_id in graph_service.thread_configs,
        "active_task": thread_id in graph_service.active_threads,
        "task_done": graph_service.active_threads[thread_id].done() if thread_id in graph_service.active_threads else None
    }