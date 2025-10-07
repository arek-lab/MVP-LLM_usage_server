import re
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, ModelSettings, function_tool
from pydantic import BaseModel, Field

load_dotenv()
MODEL = os.getenv("OPENAI_MODEL")

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
  
client = AsyncOpenAI()
@function_tool
async def check_moderation_tool(user_prompt: str) -> bool:
    """
    Tool do sprawdzania treści pod względem moderacji treści, wulgaryzmów i poszanowania drugiego człowieka.
    Zwraca True, jeśli tekst narusza zasady.
    """

    # --- Etap 2: Moderacja OpenAI z omni-moderation-latest ---
    try:
        response = await client.moderations.create(
            model="omni-moderation-latest", 
            input=user_prompt
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
    
INSTRUCTIONS = '''
Twoim zadaniem jest ocenić, czy wejściowy tekst od użytkownika może zostać użyty jako baza do stworzenia maila biznesowego.

1. **Bezpieczeństwo i moderacja**
   - Sprawdź treść przy użyciu `check_moderation_tool`.
   - Jeśli zawiera wulgaryzmy, mowę nienawiści, przemoc, dyskryminację lub inne niedozwolone elementy — oznacz jako **nieodpowiednią** i zakończ ocenę.

2. **Ocena sensowności treści**
   - Odrzuć tekst, jeśli jest ewidentnie nonsensowny, prześmiewczy, fikcyjny lub nierealny (np. "zaproszenie na konferencję na Marsie" albo "spotkanie, które odbyło się w 2015 roku").
   - Odrzuć też przypadki, w których intencja użytkownika jest całkowicie niezrozumiała.

3. **Ocena wystarczalności informacji**
   - Sprawdź, czy tekst daje **minimum kontekstu**, które pozwoli wygenerować **szkielet maila z placeholderami**.
   - Wystarczy, że można z niego wywnioskować **ogólny typ komunikatu** (np. zaproszenie, informacja, oferta, przypomnienie).
   - Brakujące szczegóły (np. data, miejsce, nazwa wydarzenia, adresaci) mogą być później uzupełnione placeholderami — **nie odrzucaj tekstu z tego powodu**.

4. **Decyzja końcowa**
   - Jeśli tekst:
     - jest zgodny z zasadami bezpieczeństwa,
     - nie jest nonsensowny ani prześmiewczy,
     - zawiera minimalny kontekst do stworzenia maila z placeholderami,
     → oznacz go jako **odpowiedni do dalszego generowania**.
   - W przeciwnym razie — oznacz jako **nieodpowiedni**.

5. **Uwagi dodatkowe**
   - Nie komentuj treści, jeśli nie stwierdzono naruszeń.
   - Celem jest przepuszczenie każdego sensownego inputu, który da się później rozwinąć w profesjonalny mail (nawet jeśli jest bardzo skrótowy).
'''


class CheckingResponse(BaseModel):
    user_query: str = Field(description="Oryginalny, niezmieniony wejściowy tekst od użytkownika")
    output_MD: str = Field(description="Odpowiedź agenta zawierająca informację o naruszeniu zasad, lub o brakach uniemożliwiajacych dalsze procesowanie z wylistowaniem braków. Oczekiwany format to MD")
    validation_pass: bool = Field("Jeżeli dane naruszają zasady lub są niewystarczające do stworzenia maila oznacz 'validation_pass' jako False, w przeciwnym wypadku oznacz jako True.")
    

input_check_agent = Agent(
    name="Input Data Checker",  
    instructions=INSTRUCTIONS,
    model=MODEL,
    output_type=CheckingResponse
)
