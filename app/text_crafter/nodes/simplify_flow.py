from app.text_crafter.state import State
from app.text_crafter.chains.simplify_flow.chain import get_simplify_chain
from app.text_crafter.chains.model import LLMResponseModel

async def simplify_flow(state: State) -> State:
    chain =get_simplify_chain(
        subcategory=state["subcategory"],
        content=state["current_text"],
        target_audience = state.get("options", {}).get("target_audience"),
        preserve_meaning = state.get("options", {}).get("preserve_meaning")
    )
    
    result: LLMResponseModel = await chain.ainvoke({})

    return {
    'result': result,
    'current_text': result.text
}