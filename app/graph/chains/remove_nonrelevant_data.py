from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.graph.chains.cv_data_model import CVData
from app.config import OPENAI_API_KEY, GPT_MODEL

def get_llm():
    return ChatOpenAI(
        api_key=OPENAI_API_KEY,
        model=GPT_MODEL,
        temperature=0,
    )
structured_llm = get_llm().with_structured_output(CVData)

system = '''Jesteś ekspertem w przetwarzaniu danych strukturalnych CV.

KONTEKST:
Otrzymasz dane CV w postaci struktury BaseModel (Pydantic) oraz listę elementów do usunięcia.

ZADANIE:
Usuń z danych CV wszystkie elementy oznaczone jako nierelewantne, zachowując pełną strukturę danych.

INSTRUKCJE:
1. Przeanalizuj dokładnie listę elementów do usunięcia
2. Przeszukaj całą strukturę CV (włącznie z zagnieżdżonymi obiektami i listami)
3. Dla każdego znalezionego elementu do usunięcia:
   - Jeśli to pole opcjonalne: ustaw wartość null/None
   - Jeśli to element listy: usuń go z listy (nie zamieniaj na None)
   - Jeśli to obiekt zagnieżdżony: usuń go lub ustaw na null/None
4. NIE modyfikuj żadnych innych danych poza wskazanymi do usunięcia
5. Zachowaj oryginalną strukturę i typy danych BaseModel
6. Zwróć kompletny obiekt CV z zachowaniem wszystkich pól (poza usuniętymi)

WAŻNE:
- Zachowaj identyczną strukturę jak w danych wejściowych
- Nie zmieniaj kolejności pól ani ich nazw
- Nie dodawaj żadnych nowych pól
- Jeśli masz wątpliwości czy dany element usunąć - NIE usuwaj go

FORMAT WYJŚCIOWY:
Zwróć pełny obiekt CV w tym samym formacie BaseModel co dane wejściowe.
'''

remove_nonrelevenat_data_prompt = ChatPromptTemplate.from_messages(
  [
    ("system", system),
    ("human", "Usuń poniższe dane z danych CV. Są nierelewantne do oferty. Dane do usunięcia:\n\n{irrelevant_information}.\nDane kompletne:\n\n{accepted_cv_data}")
  ]
)

remove_nonrelevenat_data_chain = remove_nonrelevenat_data_prompt | structured_llm
