import asyncio
import json
from typing import List, Dict, Any
from datetime import datetime

from app.loveable_features.graph.state import State
from app.loveable_features.graph.graph import graph

class DateTimeEncoder(json.JSONEncoder):
    """Custom encoder który radzi sobie z datetime i innymi typami"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        return super().default(obj)
    
def group_results(results: List[Dict]) -> Dict:
    grouped = {"leads": [], "no_leads": [], "errors": []}
    total_credits = 0
    
    for r in results:
        if r.get("status") == "error":
            grouped["errors"].append({
                "message": r.get("candidate"),
                "error": r.get("error"),
            })
            continue
        
        if r.get("status") != "success":
            continue
        
        result = r.get("result", {})
        
        # Sumuj credits ze stanu
        credits = result.get("credits", 0)
        if isinstance(credits, (int, float)):
            total_credits += credits
        
        lead_judge = result.get("lead_judge")
        if lead_judge is None:
            continue
        
        entry = {
            "original_message": result.get("message"),
            "message": result["message"].get("message"),
            "user": result["message"].get("user"),
            "is_lead": result["lead_judge"].is_lead,
            "rag_insight": result.get("rag_insight", None),
            "reply": result["reply"].reply,
        }
        
        if lead_judge.is_lead:
            grouped["leads"].append(entry)
        else:
            grouped["no_leads"].append(entry)
    
    return {
        "results": grouped,
        "total_credits": total_credits,
    }

async def process_candidates_with_batching(
    candidates: List[Dict],
    max_concurrent: int = 15,
    batch_size: int = 20
) -> Dict:
    semaphore = asyncio.Semaphore(max_concurrent)
    results = []
    
    async def process_with_semaphore(candidate: Dict, index: int) -> Dict[str, Any]:
        async with semaphore:
            try:
                result: State = await graph.ainvoke({"message": candidate})
                return {
                    "index": index,
                    "candidate": candidate,
                    "result": result,
                    "status": "success",
                }
            except Exception as e:
                return {
                    "index": index,
                    "candidate": candidate,
                    "error": str(e),
                    "status": "error",
                }
    
    tasks = [process_with_semaphore(candidate, i) for i, candidate in enumerate(candidates)]
    
    for i, coro in enumerate(asyncio.as_completed(tasks)):
        result = await coro
        results.append(result)
    
    return group_results(results)

