SYSTEM_PROMPT = """Jesteś ekspertem w skracaniu i kondensowaniu tekstów.

Twoje zadanie:
- Zachować kluczowe informacje i intencję komunikatu
- Usunąć redundancje, wypełniacze i zbędne detale
- Utrzymać naturalny, czytelny język
- Zachować wszystkie istotne liczby, daty i fakty
- Dopasować poziom skrócenia do podkategorii

Zawsze zwracaj tekst w tym samym języku co oryginał.

TWOJA ODPOWIEDŹ:
Zwróć structured output zawierający:
1. text - przepisany tekst gotowy do użycia
2. confidence - Twoją ocenę jakości przepisania (0-1), gdzie 1.0 oznacza idealne przepisanie
"""


SUBCATEGORY_INSTRUCTIONS = {
    "brief_summary": """
Stwórz bardzo zwięzłe streszczenie - maksymalnie 2-3 zdania.
Skup się tylko na najważniejszych punktach i konkluzji.
""",
    
    "remove_fluff": """
Usuń zbędne słowa i frazy, ale zachowaj pełną treść merytoryczną.
Eliminuj: powtórzenia, wypełniacze typu "w zasadzie", "można powiedzieć że", nadmiernie opisowe fragmenty.
Zachowaj: wszystkie fakty, dane liczbowe, kluczowe argumenty.
""",
    
    "key_points": """
Wyciągnij i przedstaw tylko najważniejsze punkty w formie zwartych stwierdzeń.
Każdy punkt powinien być samowystarczalny i konkretny.
Zachowaj logiczny porządek informacji.
""",
    
    "executive_summary": """
Stwórz profesjonalne executive summary w stylu biznesowym.
Zacznij od głównej konkluzji/rekomendacji, potem kluczowe fakty wspierające.
Maksymalnie 4-5 zdań, ale wszystkie krytyczne informacje muszą być obecne.
"""
}


def get_shorten_prompt(
    subcategory: str,
    content: str,
    target_length: str = None,
    preserve_tone: bool = True
) -> str:
    """
    Generuje user prompt dla skracania tekstu.
    
    Args:
        subcategory: Typ skracania (brief_summary, remove_fluff, etc.)
        content: Tekst do skrócenia
        target_length: Docelowa długość ("very_short", "short", "medium") - opcjonalne
        preserve_tone: Czy zachować ton oryginalnego tekstu
    """
    
    instruction = SUBCATEGORY_INSTRUCTIONS.get(
        subcategory, 
        "Skróć ten tekst zachowując najważniejsze informacje."
    )
    
    prompt_parts = [instruction]
    
    if target_length:
        length_guide = {
            "very_short": "Docelowa długość: maksymalnie 30% oryginalnej długości.",
            "short": "Docelowa długość: około 50% oryginalnej długości.",
            "medium": "Docelowa długość: około 70% oryginalnej długości."
        }
        if target_length in length_guide:
            prompt_parts.append(length_guide[target_length])
    
    if preserve_tone:
        prompt_parts.append("Zachowaj ton i styl oryginalnego tekstu (formalny/nieformalny).")
    
    prompt_parts.append(f"\nTekst do skrócenia:\n{content}")
    
    return "\n".join(prompt_parts)