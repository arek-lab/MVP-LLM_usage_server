# chains/simplify/prompts.py

SYSTEM_PROMPT = """Jesteś ekspertem w upraszczaniu tekstów i tłumaczeniu skomplikowanych treści na prosty, zrozumiały język.

Twoje zadanie:
- Zamienić trudne słowa i żargon na proste, powszechnie znane odpowiedniki
- Rozbić długie, złożone zdania na krótsze i klarowniejsze
- Wyjaśnić skomplikowane koncepcje w sposób przystępny
- Zachować dokładność merytoryczną i kluczowe informacje
- Używać konkretnych przykładów zamiast abstrakcji tam gdzie to możliwe
- Unikać strony biernej i skomplikowanych konstrukcji gramatycznych

Zawsze zwracaj tekst w tym samym języku co oryginał.

TWOJA ODPOWIEDŹ:
Zwróć structured output zawierający:
1. text - uproszczony tekst gotowy do użycia
2. confidence - Twoją ocenę jakości uproszczenia (0-1), gdzie 1.0 oznacza idealne uproszczenie przy zachowaniu sensu
"""


SUBCATEGORY_INSTRUCTIONS = {
    "reduce_jargon": """
Zamień wszystkie specjalistyczne terminy, skróty i żargon branżowy na proste, zrozumiałe dla każdego słowa.
Jeśli termin nie ma prostego odpowiednika, wyjaśnij go w nawiasie lub dodaj krótkie wyjaśnienie.
Przykład: "API" → "interfejs programistyczny (sposób komunikacji między programami)"
""",
    
    "shorter_sentences": """
Rozbij długie, złożone zdania na szereg krótszych zdań.
Każde zdanie powinno zawierać jedną główną myśl.
Preferuj zdania do 15-20 słów maksymalnie.
Unikaj wielokrotnie złożonych konstrukcji gramatycznych.
""",
    
    "everyday_language": """
Przepisz tekst używając wyłącznie słów z codziennego, potocznego języka.
Zamień formalne i naukowe sformułowania na naturalne, rozmówkowe wyrażenia.
Unikaj pasywu - używaj aktywnej formy czasowników.
Pisz jakbyś opowiadał coś znajomemu przy kawie.
""",
    
    "explain_concepts": """
Zidentyfikuj wszystkie trudne lub abstrakcyjne koncepcje i wyjaśnij je prostym językiem.
Dodaj konkretne przykłady lub analogie do codziennego życia.
Upewnij się, że osoba bez specjalistycznej wiedzy zrozumie każdą część tekstu.
""",
    
    "lower_reading_level": """
Uprość tekst do poziomu czytelności odpowiedniego dla ucznia szkoły podstawowej (ok. 10-12 lat).
Używaj tylko najprostszych, najczęściej spotykanych słów.
Zdania maksymalnie 10-12 słów.
Unikaj wszelkich skomplikowanych pojęć - jeśli są konieczne, wyjaśnij je jak dziecku.
"""
}


def get_simplify_prompt(
    subcategory: str,
    content: str,
    target_audience: str = None,
    preserve_meaning: bool = True,
    add_examples: bool = False
) -> str:
    """
    Generuje user prompt dla upraszczania tekstu.
    
    Args:
        subcategory: Typ uproszczenia (reduce_jargon, shorter_sentences, etc.)
        content: Tekst do uproszczenia
        target_audience: Docelowa grupa odbiorców (np. "dzieci", "seniorzy", "osoby bez wiedzy technicznej")
        preserve_meaning: Czy zachować precyzję merytoryczną (vs maksymalne uproszczenie)
        add_examples: Czy dodawać konkretne przykłady do trudnych pojęć
    """
    
    instruction = SUBCATEGORY_INSTRUCTIONS.get(
        subcategory, 
        "Uprość ten tekst tak, aby był zrozumiały dla każdego, zachowując przy tym kluczowe informacje."
    )
    
    prompt_parts = [instruction]
    
    if target_audience:
        audience_guide = {
            "dzieci": "Upraszczaj tekst tak, jakbyś tłumaczył go 10-letniemu dziecku. Używaj bardzo prostych słów i krótkich zdań.",
            "seniorzy": "Upraszczaj tekst dla osób starszych, które mogą nie znać nowoczesnego żargonu technologicznego. Używaj jasnego, bezpośredniego języka.",
            "osoby bez wiedzy technicznej": "Upraszczaj tekst dla osób bez specjalistycznej wiedzy. Każdy termin techniczny musi być wyjaśniony prostym językiem.",
            "ogół społeczeństwa": "Upraszczaj tekst dla przeciętnego czytelnika. Unikaj założeń o specjalistycznej wiedzy odbiorcy."
        }
        audience_instruction = audience_guide.get(target_audience.lower(), 
            f"Upraszczaj tekst dla grupy docelowej: {target_audience}")
        prompt_parts.append(audience_instruction)
    
    if preserve_meaning:
        prompt_parts.append("WAŻNE: Zachowaj precyzję merytoryczną - nie możesz zmienić faktów ani pominąć kluczowych informacji, nawet jeśli są skomplikowane.")
    else:
        prompt_parts.append("Priorytetem jest maksymalna prostota - możesz pominąć bardzo techniczne detale, jeśli nie są kluczowe dla głównego przekazu.")
    
    if add_examples:
        prompt_parts.append("Dodaj konkretne, życiowe przykłady do trudnych koncepcji, aby ułatwić zrozumienie.")
    
    prompt_parts.append(f"\nTekst do uproszczenia:\n{content}")
    
    return "\n".join(prompt_parts)