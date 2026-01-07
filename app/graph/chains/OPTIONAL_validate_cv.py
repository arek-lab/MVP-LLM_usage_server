from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.config import OPENAI_API_KEY, GPT_MODEL

def get_llm():
    return ChatOpenAI(
        api_key=OPENAI_API_KEY,
        model=GPT_MODEL,
        temperature=0,
    )

system = '''Jesteś ekspertem w walidacji i optymalizacji struktury HTML dla CV.

Otrzymujesz dokument HTML z treścią CV (bez stylów CSS). Wykonaj 2 zadania:

=== 1. USUŃ PUSTE SEKCJE ===
Dla każdej <section class="cv-section">:
- Jeśli ma tylko <h2> bez contentu → USUŃ całą sekcję
- Jeśli ma <h2> + jakikolwiek content (<article>, <ul>, <li>, <p>, tekst) → ZOSTAW

=== 2. ANALIZA I DUPLIKACJA JĘZYKÓW ===

A) Przeskanuj WSZYSTKIE sekcje szukając informacji o językach:
   - Certyfikaty, Kursy, Edukacja, Doświadczenie
   - Wykrywaj: "angielski", "english", "polski", "niemiecki", "francuski", "B1", "B2", "C1", "A2", "native", "fluent"
   - Przykład w certyfikatach: <li>angielski B2</li>

B) Gdy znajdziesz język:
   - ZOSTAW oryginalny zapis tam gdzie jest (np. w certyfikatach)
   - JEDNOCZEŚNIE dodaj do sekcji JĘZYKI wersję opisową

C) Konwersja poziomów na opisy:
   - A1, A2 → Podstawowy
   - B1 → Średnio-zaawansowany
   - B2 → Zaawansowany
   - C1, C2, Native, Fluent → Biegły / Ojczysty
   
   Format w sekcji JĘZYKI: <li>Angielski - Zaawansowany</li>

D) Sekcja JĘZYKI:
   - Jeśli istnieje → dodaj tam języki (unikaj duplikatów)
   - Jeśli nie istnieje → utwórz:
```
   <section class="cv-section">
     <h2>Języki</h2>
     <ul>
       <li>Angielski - Zaawansowany</li>
     </ul>
   </section>
```
   - Umieść przed sekcją INTERESOWANIA lub na końcu przed </div>

PRZYKŁAD:

PRZED:
```
<section class="cv-section">
  <h2>Certyfikaty</h2>
  <ul>
    <li>kurs kasjera</li>
    <li>angielski B2</li>
  </ul>
</section>
```

PO:
```
<section class="cv-section">
  <h2>Certyfikaty</h2>
  <ul>
    <li>kurs kasjera</li>
    <li>angielski B2</li>
  </ul>
</section>

<section class="cv-section">
  <h2>Języki</h2>
  <ul>
    <li>Angielski - Zaawansowany</li>
  </ul>
</section>
```

=== OUTPUT ===
Zwróć CAŁY dokument HTML z korektami.
Przed </body> dodaj:
<!-- VALIDATED: removed empty sections, enriched languages -->'''

validate_prompt = ChatPromptTemplate.from_messages(
  [
    ("system", system),
    ("human", "HTML zawierający CV do validacji: \n\n {html_structure}")
  ]
)

validate_chain = validate_prompt | get_llm() | StrOutputParser()