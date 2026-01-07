from app.graph.state import State
from langgraph.types import interrupt
from app.graph.chains.collect_all_cv_data import collect_all_data_chain
from app.graph.chains.remove_nonrelevant_data import remove_nonrelevenat_data_chain

async def collect_all_cv_data(state: State) -> State:
    accepted = state.get("accepted_cv_data")
    if accepted:
        if getattr(state["additional_info_human_feedback"], "removal_acceptance", None):
          result = await remove_nonrelevenat_data_chain.ainvoke(
            {
              "accepted_cv_data": accepted,
              "irrelevant_information": state["comparison_result"].irrelevant_information
            }
          )
          return {"accepted_cv_data": result}
        return {"accepted_cv_data": accepted}

    extracted_cv = state["extracted_cv"]
    comparison_result = state["comparison_result"]
    additional_info = state.get("additional_info_human_feedback")

    result = await collect_all_data_chain.ainvoke({
        "extracted_cv": extracted_cv,
        "comparison_result": comparison_result,
        "additional_info_human_feedback": additional_info
    })

    return interrupt(
        {
            "accepted_cv_data": result
        },
        
    )
