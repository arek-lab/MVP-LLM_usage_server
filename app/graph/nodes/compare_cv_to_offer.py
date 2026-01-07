from app.graph.state import State
from app.graph.chains.compare_cv_to_offer import compare_chain, ComparisonResult


async def compare_cv_to_offer(state: State) -> State:
    job_offer_description = state["job_offer_description"]
    extracted_cv = state["extracted_cv"]

    result: ComparisonResult = await compare_chain.ainvoke(
        {"job_offer_description": job_offer_description, "extracted_cv": extracted_cv}
    )

    return {"comparison_result": result}
