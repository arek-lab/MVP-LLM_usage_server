"""
SSE streaming endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sse_starlette.sse import EventSourceResponse
import json
import asyncio
import logging

from app.graph.state import FileResult
from app.services.graph_service import GraphService
from app.services.graph_dependencies import get_graph_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/events/{thread_id}")
async def stream_events(
    thread_id: str,
    graph_service: GraphService = Depends(get_graph_service)
):
    """
    Stream graph status updates via SSE
    
    Continuously streams status updates until graph completion.
    Handles multiple HITL cycles - does NOT close connection on waiting_hitl.
    
    Events:
    - status_update: regular status changes
    - hitl_required: when human input is needed (includes HITL data)
    - completed: graph finished successfully
    - error: error occurred
    """
    
    async def event_generator():
        try:
            previous_status = None
            previous_node = None
            consecutive_errors = 0
            max_consecutive_errors = 5
            
            while True:
                try:
                    # Get current status
                    status = await graph_service.get_status(thread_id)
                    
                    # Reset error counter on successful status check
                    consecutive_errors = 0
                    
                    current_status = status.get("status")
                    current_node = status.get("next_node")
                    
                    # FINAL STATES - always break after sending
                    if current_status == "completed":
                        if previous_status != "completed":
                            result = status.get("result", {})
                            
                            response_data = {
                                "status": "completed",
                                "message": "CV generated successfully"
                            }
                            
                            # Pydantic automatycznie serializuje do dict
                            if "pdf_result" in result:
                                pdf_result = result["pdf_result"]
                                # Jeśli to już FileResult, konwertuj do dict
                                if isinstance(pdf_result, FileResult):
                                    response_data["result"] = pdf_result.model_dump()
                                else:
                                    response_data["result"] = pdf_result
                            
                            yield {
                                "event": "completed",
                                "data": json.dumps(response_data, ensure_ascii=False)
                            }
                        break
                    
                    if current_status == "error":
                        # Only send if this is a new state
                        if previous_status != "error":
                            yield {
                                "event": "error",
                                "data": json.dumps({
                                    "status": "error",
                                    "error": status.get("error", "Unknown error occurred"),
                                    "error_details": status.get("error_details")
                                }, default=str, ensure_ascii=False)
                            }
                        break
                    
                    # Handle waiting_hitl status
                    if current_status == "waiting_hitl":
                        # Send HITL event only when entering this state
                        if previous_status != "waiting_hitl":
                            yield {
                                "event": "hitl_required",
                                "data": json.dumps({
                                    "status": current_status,
                                    "hitl_type": status.get("hitl_type"),
                                    "hitl_data": status.get("hitl_data"),
                                    "next_node": current_node,
                                    "message": "Human input required"
                                }, default=str, ensure_ascii=False)
                            }
                            previous_status = current_status
                            previous_node = current_node
                        
                        # Continue polling - graph will resume after HITL submission
                        await asyncio.sleep(2)
                        continue
                    
                    # Handle transition from waiting_hitl to running
                    if previous_status == "waiting_hitl" and current_status not in ["waiting_hitl", "completed", "error"]:
                        yield {
                            "event": "status_update",
                            "data": json.dumps({
                                "status": current_status,
                                "next_node": current_node,
                                "message": "Graph resumed after HITL"
                            }, default=str, ensure_ascii=False)
                        }
                        previous_status = current_status
                        previous_node = current_node
                        await asyncio.sleep(2)
                        continue
                    
                    # Send update if status or node changed (and not already handled above)
                    if (current_status != previous_status or current_node != previous_node):
                        yield {
                            "event": "status_update",
                            "data": json.dumps({
                                "status": current_status,
                                "next_node": current_node
                            }, default=str, ensure_ascii=False)
                        }
                        
                        previous_status = current_status
                        previous_node = current_node
                    
                except ValueError as e:
                    # Thread not found or invalid
                    logger.error(f"Thread {thread_id} error: {e}")
                    yield {
                        "event": "error",
                        "data": json.dumps({
                            "error": f"Thread error: {str(e)}",
                            "error_type": "not_found"
                        })
                    }
                    break
                    
                except Exception as e:
                    # Unexpected error during status check
                    consecutive_errors += 1
                    logger.warning(f"Status check error for {thread_id} (attempt {consecutive_errors}): {e}")
                    
                    # If too many consecutive errors, give up
                    if consecutive_errors >= max_consecutive_errors:
                        logger.error(f"Too many consecutive errors for {thread_id}, closing stream")
                        yield {
                            "event": "error",
                            "data": json.dumps({
                                "error": f"Persistent error checking status: {str(e)}",
                                "error_type": "status_check_failed"
                            })
                        }
                        break
                    
                    # Otherwise continue with longer backoff
                    await asyncio.sleep(3)
                    continue
                
                # Wait before next check
                await asyncio.sleep(2)
                
        except asyncio.CancelledError:
            # Client disconnected - clean exit
            logger.info(f"SSE stream cancelled for thread {thread_id}")
            pass
        except Exception as e:
            # Fatal stream error
            logger.error(f"Fatal SSE stream error for {thread_id}: {e}")
            yield {
                "event": "error",
                "data": json.dumps({
                    "error": f"Stream error: {str(e)}",
                    "error_type": "fatal"
                })
            }
    
    return EventSourceResponse(event_generator())


@router.get("/events/{thread_id}/health")
async def stream_health_check(
    thread_id: str,
    graph_service: GraphService = Depends(get_graph_service)
):
    """
    Quick health check for SSE stream
    Verifies thread exists before establishing long connection
    """
    try:
        await graph_service.get_status(thread_id)
        return {"status": "ok", "thread_id": thread_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")