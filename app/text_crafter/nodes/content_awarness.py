import re
from app.text_crafter.state import State, Flags

# bardzo prosta lista startowa — DO ROZBUDOWY
PROFANITY_LIST = [
    "fuck",
    "shit",
    "kurw",
    "chuj",
    "pizd",
    "jeb",
    "pierdol",
    "skurw",
    "ciul",
    "suk",
    "fuck",
    "shit",
    "dziw",
    "cwel",
    "szmat",
    "debil",
    "idiot",
    "kretyn",
    "pojeb",
    "zjeb",
    "nienawidz",
    "nienawisc",
    "spierdal",
    "wypierdal",
    "wyjeb",
    "rozjeb",
    "dojeb",
    "napierdal",
    "kurwiarz",
]

profanity_regex = re.compile(
    r"\b(" + "|".join(PROFANITY_LIST) + r")[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ]*\b",
    re.IGNORECASE,
)


def content_awareness(state: State) -> State:
    text = state["current_text"] or ""

    contains_profanity = bool(profanity_regex.search(text))

    # ALL CAPS detection (ignorujemy krótkie teksty)
    letters_only = re.sub(r"[^A-Za-z]", "", text)
    is_all_caps = len(letters_only) >= 10 and letters_only.isupper()

    # Nadmiar wykrzykników / znaków
    has_excessive_punctuation = bool(re.search(r"[!?]{3,}", text))

    flags: Flags = {
        "contains_profanity": contains_profanity,
        "is_all_caps": is_all_caps,
        "has_excessive_punctuation": has_excessive_punctuation,
    }

    return {
        **state,
        "flags": flags,
    }
