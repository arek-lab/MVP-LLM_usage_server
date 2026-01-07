from app.graph.state import State
from langgraph.types import interrupt


async def human_review(state: State) -> State:
    feedback_from_state = state.get("additional_info_human_feedback")
    
    if feedback_from_state:
        print("🚀 Otrzymano dane zwrotne.")
        return {"human_feedback": feedback_from_state}

    result = state["comparison_result"]

    # tu dodajemy NAME interruptu!
    return interrupt(
        {
            "comparison_result": result.model_dump(),
            "message": "Proszę zweryfikować porównanie CV z ofertą pracy"
        },
    )

