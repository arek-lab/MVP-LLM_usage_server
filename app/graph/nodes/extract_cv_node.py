from app.graph.state import State
from app.graph.chains.extract_cv_data import extract_chain


async def extract_cv_node(state: State) -> State:
    cv_text = state["cv_text"]

    result = await extract_chain.ainvoke({"cv_text": cv_text})

    return {"extracted_cv": result}
