from app.text_crafter.state import State
from langgraph.graph import StateGraph, START, END

from app.text_crafter.nodes.normalize_input import normalize_input
from app.text_crafter.nodes.content_awarness import content_awareness
from app.text_crafter.nodes.route_by_intent import route_by_intent
from app.text_crafter.nodes.default_flow import default_flow
from app.text_crafter.nodes.rewrite_flow import rewrite_flow
from app.text_crafter.nodes.shorten_flow import shorten_flow
from app.text_crafter.nodes.tone_flow import tone_flow
from app.text_crafter.nodes.simplify_flow import simplify_flow
from app.text_crafter.nodes.quality_check import quality_check


def build_graph():
    flow = StateGraph(State)

    flow.add_node("input", normalize_input)
    flow.add_node("content_check", content_awareness)
    flow.add_node("rewrite_flow", rewrite_flow)
    flow.add_node("shorten_flow", shorten_flow)
    flow.add_node("tone_flow", tone_flow)
    flow.add_node("simplify_flow", simplify_flow)
    flow.add_node("default_flow", default_flow)
    flow.add_node("quality_check", quality_check)

    flow.add_edge(START, "input")
    flow.add_edge("input", "content_check")
    flow.add_conditional_edges(
        "content_check",
        route_by_intent,
        {
            "rewrite_flow": "rewrite_flow",
            "shorten_flow": "shorten_flow",
            "tone_flow": "tone_flow",
            "simplify_flow": "simplify_flow",
            "default_flow": "default_flow",
        },
    )
    flow.add_edge("rewrite_flow", "quality_check")
    flow.add_edge("shorten_flow", "quality_check")
    flow.add_edge("tone_flow", "quality_check")
    flow.add_edge("simplify_flow", "quality_check")
    flow.add_edge("default_flow", "quality_check")
    flow.add_edge("quality_check", END)


    return flow.compile()

graph = build_graph()