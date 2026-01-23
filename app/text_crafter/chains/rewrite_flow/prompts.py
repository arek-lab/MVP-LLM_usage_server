# chains/rewrite/prompts.py

SYSTEM_PROMPT = """Jesteś ekspertem od przepisywania i edycji tekstów w języku polskim i angielskim.

ZASADY:
- Zachowaj oryginalny sens i kluczowe informacje z tekstu
- Nie dodawaj nowych faktów ani informacji, których nie ma w oryginale
- Rozpoznaj język tekstu wejściowego i odpowiedz w tym samym języku
- Jeśli tekst zawiera specjalistyczne terminy techniczne, zachowaj je (chyba że instrukcja wymaga uproszczenia)
- Zachowaj formatowanie (akapity, listy) jeśli ma sens w kontekście zadania

TWOJA ODPOWIEDŹ:
Zwróć structured output zawierający:
1. text - przepisany tekst gotowy do użycia
2. confidence - Twoją ocenę jakości przepisania (0-1), gdzie 1.0 oznacza idealne przepisanie
"""

REWRITE_INSTRUCTIONS = {
    "formal_to_informal": """Przepisz poniższy tekst na bardziej swobodny, nieformalny styl.

WYTYCZNE:
- Użyj prostszych, bardziej potocznych słów
- Skróć długie, złożone zdania na krótsze
- Możesz użyć form ściągniętych (np. "it's" zamiast "it is")
- Dodaj naturalność i ciepło w tonie
- Unikaj sztywnego, korporacyjnego języka
- Zachowaj profesjonalizm, ale uczyń tekst bardziej przystępnym

Tekst do przepisania:
{content}""",
    "informal_to_formal": """Przepisz poniższy tekst na formalny, profesjonalny styl.

WYTYCZNE:
- Użyj pełnych form zamiast skrótów (np. "it is" zamiast "it's")
- Unikaj kolokwializmów i potocznych wyrażeń
- Zastosuj bardziej precyzyjne, profesjonalne słownictwo
- Wydłuż i uporządkuj strukturę zdań
- Zachowaj obiektywny, rzeczowy ton
- Usuń nadmierną emocjonalność i osobiste akcenty

Tekst do przepisania:
{content}""",
    "improve_clarity": """Przepisz poniższy tekst, czyniąc go jaśniejszym i bardziej zrozumiałym.

WYTYCZNE:
- Uprość złożone zdania na krótsze, przejrzyste struktury
- Zastąp żargon i skomplikowane terminy prostszymi odpowiednikami (jeśli to możliwe)
- Usuń wieloznaczności i niejasne sformułowania
- Popraw logiczny przepływ myśli
- Wyeliminuj redundancje i powtórzenia
- Uporządkuj informacje w bardziej logicznej kolejności

Tekst do przepisania:
{content}""",
    "audience_adaptation": """Przepisz poniższy tekst, dostosowując go do następującego odbiorcy: {target_audience}

WYTYCZNE:
- Dobierz odpowiedni poziom szczegółowości dla tej grupy
- Dostosuj słownictwo i przykłady do ich kontekstu
- Uwzględnij ich wiedzę i oczekiwania
- Dla ekspertów: możesz użyć terminologii branżowej
- Dla ogółu: uprość i dodaj wyjaśnienia
- Dla kadry zarządzającej: skup się na high-level insights i implikacjach biznesowych

Tekst do przepisania:
{content}""",
    "creative_rephrase": """Przepisz poniższy tekst w bardziej angażujący, świeży sposób.

WYTYCZNE:
- Zachowaj to samo znaczenie, ale użyj bardziej żywego języka
- Zastosuj silniejsze, bardziej obrazowe słownictwo
- Dodaj element storytellingu tam, gdzie to naturalne
- Uczyń tekst bardziej przekonującym i interesującym
- Możesz zmienić strukturę zdań dla lepszego flow
- Zachowaj autentyczność - nie przesadzaj z "marketingowym" brzmieniem

Tekst do przepisania:
{content}""",
    "platform_adaptation": """Przepisz poniższy tekst, dostosowując go do platformy: {target_platform}

WYTYCZNE WEDŁUG PLATFORMY:

LinkedIn:
- Profesjonalny, ale przystępny ton
- Zastosuj krótkie akapity (2-3 zdania max)
- Rozpocznij od hook'a, który zatrzyma scrollowanie
- Możesz użyć emoji, ale oszczędnie
- Zakończ call-to-action lub pytaniem angażującym

Email:
- Jasna linia tematyczna (jeśli dotyczy)
- Bezpośredni, zwięzły język
- Wyraźna struktura z akapitami
- Zakończ konkretnym next step

Twitter/X:
- Maksymalna zwięzłość
- Usuń zbędne słowa
- Zachowaj kluczowy message
- Możesz podzielić na wątki jeśli tekst jest długi

Blog:
- Naturalny, conversational ton
- Dłuższe akapity są OK
- Dodaj podtytuły jeśli tekst jest długi
- Storytelling i przykłady

Tekst do przepisania:
{content}""",
    "expand": """Rozwiń poniższy tekst, dodając więcej szczegółów i kontekstu.

WYTYCZNE:
- Rozbuduj kluczowe punkty o dodatkowe wyjaśnienia
- Dodaj konkretne przykłady ilustrujące główne tezy
- Wpleć dodatkowy kontekst pomagający zrozumieć temat
- Rozwiń skróty myślowe w pełne wyjaśnienia
- Zachowaj spójność i logiczny przepływ
- Nie dodawaj informacji sprzecznych z oryginałem

Tekst do przepisania:
{content}""",
    "make_persuasive": """Przepisz poniższy tekst, czyniąc go bardziej przekonującym.

WYTYCZNE:
- Wzmocnij argumenty o konkretne korzyści
- Użyj technik perswazji (social proof, scarcity, authority - tam gdzie pasują)
- Zacznij od mocnego otwarcia
- Dodaj emocjonalny wymiar do racjonalnych argumentów
- Zakończ wyraźnym wezwaniem do działania
- Zachowaj wiarygodność - nie przesadzaj z obietnicami

Tekst do przepisania:
{content}""",
    "passive_to_active": """Przepisz poniższy tekst, zamieniając strony bierne na czynne.

WYTYCZNE:
- Zamień konstrukcje "został zrobiony przez" na "X zrobił"
- Wskaż jasno, kto wykonuje akcję
- Uczyń tekst bardziej dynamicznym i bezpośrednim
- Zachowaj sens i kontekst
- Jeśli strona bierna jest uzasadniona (np. nieznany sprawca), możesz ją zachować

Tekst do przepisania:
{content}""",
    "general": """Przepisz poniższy tekst, poprawiając jego ogólną jakość.

WYTYCZNE:
- Popraw czytelność i flow
- Wyeliminuj niezręczne sformułowania
- Zachowaj oryginalny ton i styl, ale uczyń go lepszym
- Usuń błędy stylistyczne
- Uporządkuj strukturę jeśli jest chaotyczna

Tekst do przepisania:
{content}""",
}

# Fallback gdy subcategory jest nieznana
DEFAULT_INSTRUCTION = REWRITE_INSTRUCTIONS["general"]


def get_rewrite_prompt(subcategory: str, content: str, **kwargs) -> str:
    """
    Zwraca sformatowany prompt dla danej podkategorii rewrite.

    Args:
        subcategory: Typ przepisania (klucz z REWRITE_INSTRUCTIONS)
        content: Tekst do przepisania
        **kwargs: Dodatkowe parametry (target_audience, target_platform, etc.)

    Returns:
        Sformatowany prompt gotowy do wysłania do LLM
    """
    instruction_template = REWRITE_INSTRUCTIONS.get(subcategory, DEFAULT_INSTRUCTION)

    # Wstrzyknij content i dodatkowe parametry
    try:
        return instruction_template.format(content=content, **kwargs)
    except KeyError as e:
        # Jeśli brakuje wymaganego parametru (np. target_audience), użyj fallback
        print(
            f"Warning: Missing parameter {e} for subcategory {subcategory}, using general rewrite"
        )
        return REWRITE_INSTRUCTIONS["general"].format(content=content)
