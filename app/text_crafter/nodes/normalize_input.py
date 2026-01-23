from app.text_crafter.state import State


def normalize_input(state: State) -> State:
    if "original_text" not in state or not state["original_text"]:
        raise ValueError("original_text is required")

    text = state["original_text"].strip()

    if len(text) == 0:
        raise ValueError("original_text cannot be empty after trimming")

    # Optional: very basic length guard (cheap protection)
    if len(text) > 20_000:
        raise ValueError("original_text is too long")

    return {
        **state,
        "original_text": text,
        "current_text": state.get("current_text") or text,
    }
