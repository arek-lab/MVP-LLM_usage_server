from app.graph.chains.OPTIONAL_validate_cv import validate_chain
from app.graph.state import State

async def validate_cv(state: State) -> State:
  html_structure = state["html_structure"]
  result = await validate_chain.ainvoke(
    {"html_structure": html_structure}
  )
    
  return {"final_html_structure": result}