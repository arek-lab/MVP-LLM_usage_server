from app.text_crafter.state import State


def route_by_intent(state: State) -> str:
    """
    Zwraca nazwę flow lub node docelowego dla danego intent
    """
    intent = state["intent"].lower()

    if intent == "rewrite_flow":
        return "rewrite_flow"
    elif intent == "shorten_flow":
        return "shorten_flow"
    elif intent == "tone_flow":
        return "tone_flow"
    elif intent == "simplify_flow":
        return "simplify_flow"
    else:
        return "default_flow"
