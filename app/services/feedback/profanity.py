import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

profanity_roots = [
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
    r"\b(" + "|".join(profanity_roots) + r")[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ]*\b",
    re.IGNORECASE,
)


def contains_profanity(text: str) -> bool:
    """Sprawdza lokalnie czy tekst zawiera wulgaryzmy."""
    return bool(profanity_regex.search(text))


client = OpenAI()


def check_moderation_tool(user_prompt: str) -> bool:
    """
    Tool do sprawdzania treści pod względem moderacji treści, wulgaryzmów i poszanowania drugiego człowieka.
    Zwraca True, jeśli tekst narusza zasady.
    """

    # --- Etap 1: lokalny filtr ---
    if contains_profanity(user_prompt):
        return True

    # --- Etap 2: Moderacja OpenAI z omni-moderation-latest ---
    try:
        response = client.moderations.create(
            model="omni-moderation-latest", input=user_prompt
        )

        result = response.results[0]
        scores = result.category_scores

        # Sprawdzenie czy zostało oflagowane przez OpenAI
        if result.flagged:
            return True

        # Dodatkowe sprawdzenie progów dla różnych kategorii
        if scores.hate > 0.15:
            return True
        if scores.hate_threatening > 0.1:
            return True
        if scores.violence > 0.1:
            return True
        if scores.sexual > 0.1:
            return True

        return False

    except Exception as e:
        # W przypadku błędu API, loguj i zwróć False (lub True w zależności od strategii)
        print(f"Błąd podczas moderacji OpenAI: {e}")
        return False  # Lub True, jeśli chcesz być bardziej restrykcyjny
