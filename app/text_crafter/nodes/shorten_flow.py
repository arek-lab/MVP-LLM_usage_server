from app.text_crafter.state import State
from app.text_crafter.chains.shorten_flow.chain import get_shorten_chain
from app.text_crafter.chains.model import LLMResponseModel


async def shorten_flow(state: State) -> State:
    chain = get_shorten_chain(
        subcategory=state["subcategory"],
        content=state["current_text"],
        target_length = state.get("options", {}).get("target_length"),
        preserve_tone = state.get("options", {}).get("preserve_tone")
    )
    
    result: LLMResponseModel = await chain.ainvoke({})

    return {
    'result': result,
    'current_text': result.text
}
