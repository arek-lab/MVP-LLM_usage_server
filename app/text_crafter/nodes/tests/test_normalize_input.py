from app.text_crafter.nodes.normalize_input import normalize_input


def test_normalize_input_should_trim_and_copy_text():
    state = {
        "original_text": "  Hello world  ",
        "current_text": None,
        "intent": "rewrite",
        "options": None,
    }

    out = normalize_input(state)

    assert out["original_text"] == "Hello world"
    assert out["current_text"] == "Hello world"
