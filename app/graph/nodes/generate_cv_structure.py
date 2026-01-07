from app.graph.state import State
from app.graph.chains.generate_cv_structure import generate_cv_structure_chain

async def generate_cv_structure(state: State) -> State:
  accepted_cv_data = state['accepted_cv_data']
  
  result = await generate_cv_structure_chain.ainvoke(
    {'accepted_cv_data': accepted_cv_data}
  )
  
  # with open("cv_structure.html", "w", encoding="utf-8") as f:
    # f.write(result)
  
  return {"html_structure": result}