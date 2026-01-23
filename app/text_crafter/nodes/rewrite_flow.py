from app.text_crafter.chains.rewrite_flow.chain import get_rewrite_chain
from app.text_crafter.state import State
from app.text_crafter.chains.model import LLMResponseModel

async def rewrite_flow(state: State) -> State:
    chain = get_rewrite_chain(
        subcategory=state["subcategory"],
        content=state["current_text"],
        target_audience = state.get("options", {}).get("target_audience"),
        target_platform = state.get("options", {}).get("target_platform")
    )
    
    result: LLMResponseModel = await chain.ainvoke({})

    return {
    'result': result,
    'current_text': result.text
}