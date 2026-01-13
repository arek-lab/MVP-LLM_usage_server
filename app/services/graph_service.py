"""
Graph Service - Handles graph execution and HITL
"""
from uuid import uuid4
from typing import Dict, Any, Optional
from langchain_core.messages import HumanMessage
import asyncio
import time
import logging
from fastapi import Request
from app.graph.graph import graph

logger = logging.getLogger(__name__)

THREAD_TTL = 900  # 15 minut old threads are cleaned up

class GraphService:
    def __init__(self):
        self.active_threads: Dict[str, asyncio.Task] = {}
        self.thread_configs: Dict[str, Dict] = {}
        self.thread_created_at: Dict[str, float] = {}  # thread_id -> timestamp
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self):
        """Start the cleanup loop"""
        if not self._running:
            self._running = True
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            logger.info("GraphService cleanup loop started")

    async def stop(self):
        """Stop the cleanup loop"""
        self._running = False
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        logger.info("GraphService cleanup loop stopped")

    async def _cleanup_loop(self):
        """Simple cleanup: delete threads older than THREAD_TTL"""
        while self._running:
            try:
                now = time.time()
                for thread_id in list(self.thread_created_at.keys()):
                    age = now - self.thread_created_at[thread_id]
                    if age > THREAD_TTL:
                        logger.info(f"Cleaning up thread {thread_id} (age: {age:.0f}s)")
                        self.cleanup_thread(thread_id)
                await asyncio.sleep(30)  # Check every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}", exc_info=True)

    def cleanup_thread(self, thread_id: str):
        """Clean up thread resources"""
        if thread_id in self.active_threads:
            task = self.active_threads[thread_id]
            if not task.done():
                task.cancel()
            del self.active_threads[thread_id]

        if thread_id in self.thread_configs:
            del self.thread_configs[thread_id]

        if thread_id in self.thread_created_at:
            del self.thread_created_at[thread_id]

        logger.info(f"Cleaned up thread {thread_id}")
        
    async def start_graph(
        self, 
        cv_text: str, 
        job_offer: Optional[str] = None,
        request: Request = None,
        current_user = None
    ) -> str:
        """Start graph execution in background"""

        if current_user and request:
            from app.auth.database import get_user_database
            
            credits = current_user.credits
            
            # Sprawdź czy użytkownik ma kredyty
            if credits <= 0:
                raise ValueError("Insufficient credits")
            
            # Odejmij kredyt
            user_db = get_user_database(request)
            updated_user = await user_db.increment_credits(current_user.id, -20)
            new_credits = updated_user.credits if updated_user else credits - 20
            
            logger.info(f"Deducted 1 credit from user {current_user.id}. New balance: {new_credits}")

        thread_id = str(uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        initial_state = {
            "cv_text": cv_text,
            "job_offer_agent_messages": [HumanMessage(content=job_offer)]
        }
        
        # Store config and creation time
        self.thread_configs[thread_id] = config
        self.thread_created_at[thread_id] = time.time()
        
        # Start execution in background
        task = asyncio.create_task(self._execute_graph(initial_state, config))
        self.active_threads[thread_id] = task
        
        return thread_id
    
    async def _execute_graph(self, initial_state: Dict, config: Dict):
        """Execute graph until interrupt or completion"""
        try:
            async for _ in graph.astream(initial_state, config, stream_mode="updates"):
                pass
        except Exception as e:
            logger.error(f"[GraphService] Graph execution error: {e}", exc_info=True)
    
    async def get_status(self, thread_id: str) -> Dict[str, Any]:
        """Get current status of graph execution"""
        if thread_id not in self.thread_configs:
            raise ValueError(f"Thread {thread_id} not found")
        
        config = self.thread_configs[thread_id]
        
        try:
            snapshot = graph.get_state(config)
            
            if snapshot is None:
                logger.error(f"Snapshot is None for {thread_id}")
                return {
                    "thread_id": thread_id,
                    "status": "error",
                    "error": "Failed to get graph state: snapshot is None"
                }
                
        except Exception as e:
            logger.error(f"Failed to get graph state for {thread_id}: {e}")
            return {
                "thread_id": thread_id,
                "status": "error",
                "error": f"Failed to get graph state: {str(e)}"
            }
        
        # Check if graph has been interrupted (true HITL)
        is_interrupted = bool(snapshot.tasks and any(
            hasattr(task, 'interrupts') and task.interrupts 
            for task in snapshot.tasks
        ))
        
        # Determine basic state
        has_next = bool(snapshot.next)
        task = self.active_threads.get(thread_id)
        is_task_done = task and task.done()
        
        # Base response
        response = {
            "thread_id": thread_id,
            "next_node": snapshot.next[0] if snapshot.next else None,
        }
        
        # Check for task errors first
        if is_task_done:
            try:
                exception = task.exception()
                if exception:
                    logger.error(f"Task exception for {thread_id}: {exception}")
                    response["status"] = "error"
                    response["error"] = str(exception)
                    return response
            except asyncio.CancelledError:
                response["status"] = "cancelled"
                return response
        
        # Determine status based on graph state
        if is_interrupted and has_next:
            response["status"] = "waiting_hitl"
            interrupt_node = snapshot.next[0]
            
            if interrupt_node == "human review":
                response["hitl_type"] = "additional_info"
                comparison_result = snapshot.values.get('comparison_result') if snapshot.values else None
                response["hitl_data"] = {
                    "missing_info": comparison_result.suggested_additions if comparison_result else []
                }
                
            elif interrupt_node == "collect all data":
                response["hitl_type"] = "acceptation"
                try:
                    if snapshot.tasks and len(snapshot.tasks) > 0:
                        interrupts = getattr(snapshot.tasks[0], 'interrupts', None)
                        if interrupts and len(interrupts) > 0:
                            cv_data = interrupts[0].value.get('accepted_cv_data')
                        else:
                            cv_data = snapshot.values.get('accepted_cv_data') if snapshot.values else None
                    else:
                        cv_data = snapshot.values.get('accepted_cv_data') if snapshot.values else None

                    if cv_data:
                        if hasattr(cv_data, 'model_dump'):
                            cv_data_dict = cv_data.model_dump()
                        elif hasattr(cv_data, 'dict'):
                            cv_data_dict = cv_data.dict()
                        else:
                            cv_data_dict = cv_data
                    else:
                        cv_data_dict = None

                    response["hitl_data"] = {
                        "cv_data": cv_data_dict
                    }
                except Exception as e:
                    logger.warning(f"Could not extract cv_data from interrupts: {e}")
                    response["hitl_data"] = {
                        "cv_data": snapshot.values.get('accepted_cv_data') if snapshot.values else None
                    }
            else:
                logger.warning(f"Unknown interrupt node for {thread_id}: {interrupt_node}")
                response["hitl_type"] = "unknown"
                response["hitl_data"] = {
                    "interrupt_node": interrupt_node,
                    "available_values": list(snapshot.values.keys()) if snapshot.values else []
                }
                
        elif not has_next and is_task_done:
            response["status"] = "completed"
            response["result"] = {
            "final_html": snapshot.values.get('final_html') if snapshot.values else None,
            "pdf_result": snapshot.values.get('pdf_result') if snapshot.values else None
    }
            
        elif has_next and not is_interrupted:
            response["status"] = "running"
            
        elif not has_next and not is_task_done:
            response["status"] = "running"
            
        else:
            response["status"] = "running"
        
        return response
    
    async def handle_hitl_feedback(self, thread_id: str, feedback: Dict[str, Any]):
        """Handle HITL feedback and resume graph execution"""
        if thread_id not in self.thread_configs:
            raise ValueError(f"Thread {thread_id} not found")
        
        config = self.thread_configs[thread_id]
        
        try:
            snapshot = graph.get_state(config)
        except Exception as e:
            raise ValueError(f"Failed to get graph state: {e}")
        
        if not snapshot.next:
            raise ValueError("Graph is not waiting for input")
        
        interrupt_node = snapshot.next[0]
        
        # Handle different interrupt types
        if interrupt_node == "human review":
            human_feedback = feedback.get("additional_info")
            if not human_feedback:
                raise ValueError("additional_info is required for this HITL type")
            graph.update_state(config, {"additional_info_human_feedback": human_feedback})
            logger.info(f"Updated state with additional_info for {thread_id}")
            
        elif interrupt_node == "collect all data":
            human_feedback = feedback.get("accepted_cv_data")
            if human_feedback:
                graph.update_state(config, {"accepted_cv_data": human_feedback})
                logger.info(f"Updated state with accepted_cv_data for {thread_id}")
            else:
                try:
                    cv_data = snapshot.tasks[0].interrupts[0].value.get('accepted_cv_data')
                    graph.update_state(config, {"accepted_cv_data": cv_data})
                    logger.info(f"Updated state with existing cv_data for {thread_id}")
                except (IndexError, AttributeError):
                    raise ValueError("No accepted_cv_data provided and no existing data found")
        else:
            raise ValueError(f"Unknown interrupt node: {interrupt_node}")
        
        # Resume execution
        task = asyncio.create_task(self._execute_graph(None, config))
        self.active_threads[thread_id] = task
        logger.info(f"Resumed graph execution for {thread_id}")