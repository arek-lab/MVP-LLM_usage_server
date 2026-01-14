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
from app.auth.utils import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/events/{thread_id}")
async def stream_events(
    thread_id: str,
    graph_service: GraphService = Depends(get_graph_service),
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
        import time

        previous_status = None
        previous_node = None

        consecutive_errors = 0
        max_consecutive_errors = 5

        last_ping = time.monotonic()

        try:
            while True:
                try:
                    status = await graph_service.get_status(thread_id)
                    consecutive_errors = 0

                    current_status = status.get("status")
                    current_node = status.get("next_node")

                    # ===== FINAL STATES =====

                    if current_status == "completed":
                        if previous_status != "completed":
                            result = status.get("result", {})

                            response_data = {
                                "status": "completed",
                                "message": "CV generated successfully",
                            }

                            if "pdf_result" in result:
                                pdf_result = result["pdf_result"]
                                if isinstance(pdf_result, FileResult):
                                    response_data["result"] = pdf_result.model_dump()
                                else:
                                    response_data["result"] = pdf_result

                            if "final_html" in result:
                                response_data.setdefault("result", {})
                                response_data["result"]["final_html"] = result["final_html"]

                            yield {
                                "event": "completed",
                                "data": json.dumps(response_data, ensure_ascii=False),
                            }
                        break

                    if current_status == "error":
                        if previous_status != "error":
                            yield {
                                "event": "error",
                                "data": json.dumps(
                                    {
                                        "status": "error",
                                        "error": status.get("error", "Unknown error occurred"),
                                        "error_details": status.get("error_details"),
                                    },
                                    default=str,
                                    ensure_ascii=False,
                                ),
                            }
                        break

                    # ===== WAITING HITL =====

                    if current_status == "waiting_hitl":
                        if previous_status != "waiting_hitl":
                            yield {
                                "event": "hitl_required",
                                "data": json.dumps(
                                    {
                                        "status": current_status,
                                        "hitl_type": status.get("hitl_type"),
                                        "hitl_data": status.get("hitl_data"),
                                        "next_node": current_node,
                                        "message": "Human input required",
                                    },
                                    default=str,
                                    ensure_ascii=False,
                                ),
                            }
                            previous_status = current_status
                            previous_node = current_node

                        # heartbeat nawet gdy czekamy na człowieka
                        now = time.monotonic()
                        if now - last_ping > 10:
                            yield {"event": "ping", "data": ""}
                            last_ping = now

                        await asyncio.sleep(2.5)
                        continue

                    # ===== RESUME AFTER HITL =====

                    if previous_status == "waiting_hitl" and current_status not in (
                        "waiting_hitl",
                        "completed",
                        "error",
                    ):
                        yield {
                            "event": "status_update",
                            "data": json.dumps(
                                {
                                    "status": current_status,
                                    "next_node": current_node,
                                    "message": "Graph resumed after HITL",
                                },
                                default=str,
                                ensure_ascii=False,
                            ),
                        }
                        previous_status = current_status
                        previous_node = current_node

                    # ===== REGULAR STATUS UPDATE =====

                    if current_status != previous_status or current_node != previous_node:
                        yield {
                            "event": "status_update",
                            "data": json.dumps(
                                {
                                    "status": current_status,
                                    "next_node": current_node,
                                },
                                default=str,
                                ensure_ascii=False,
                            ),
                        }
                        previous_status = current_status
                        previous_node = current_node

                    # ===== HEARTBEAT (always) =====

                    now = time.monotonic()
                    if now - last_ping > 10:
                        yield {"event": "ping", "data": ""}
                        last_ping = now

                except ValueError as e:
                    # chwilowa niedostępność threada (restart dyno / reconnect)
                    logger.warning(f"Thread {thread_id} temporarily unavailable: {e}")
                    await asyncio.sleep(2.5)
                    continue

                except Exception as e:
                    consecutive_errors += 1
                    logger.warning(
                        f"Status check error for {thread_id} "
                        f"(attempt {consecutive_errors}): {e}"
                    )

                    if consecutive_errors >= max_consecutive_errors:
                        yield {
                            "event": "error",
                            "data": json.dumps(
                                {
                                    "error": f"Persistent error checking status: {str(e)}",
                                    "error_type": "status_check_failed",
                                },
                                ensure_ascii=False,
                            ),
                        }
                        break

                    await asyncio.sleep(3)
                    continue

                await asyncio.sleep(2.5)

        except asyncio.CancelledError:
            logger.info(f"SSE stream cancelled for thread {thread_id}")

        except Exception as e:
            logger.error(f"Fatal SSE stream error for {thread_id}: {e}")
            yield {
                "event": "error",
                "data": json.dumps(
                    {
                        "error": f"Stream error: {str(e)}",
                        "error_type": "fatal",
                    },
                    ensure_ascii=False,
                ),
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