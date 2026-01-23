from app.text_crafter.nodes.content_awarness import content_awareness


def test_content_awarness():
    state = {
        "original_text": "THIS IS FUCKING BAD!!!",
        "current_text": "THIS IS FUCKING BAD!!!",
        "intent": "rewrite",
        "options": {},
        "flags": None,
    }

    out = content_awareness(state)

    assert out["flags"]["contains_profanity"] is True
    assert out["flags"]["is_all_caps"] is True
    assert out["flags"]["has_excessive_punctuation"] is True
