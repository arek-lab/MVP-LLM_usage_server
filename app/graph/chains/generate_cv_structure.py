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

system = ''''Jesteś ekspertem w tworzeniu semantycznej struktury HTML dla CV.

Twoim zadaniem jest wygenerowanie kompletnego dokumentu HTML5 z danymi CV dostarczonymi przez użytkownika.

ZASADY:

1. Analizuj dane i twórz sekcje TYLKO dla danych, które faktycznie otrzymałeś:
   - Header (imię, nazwisko, kontakt) - ZAWSZE jeśli są dane
   - Podsumowanie/O mnie - tylko gdy jest tekst
   - Doświadczenie - tylko gdy są pozycje
   - Edukacja - tylko gdy są pozycje
   - Umiejętności - tylko gdy są
   - Projekty - tylko gdy są
   - Certyfikaty - tylko gdy są
   - Języki - tylko gdy są

2. KLUCZOWE: Jeśli dane dla sekcji NIE ISTNIEJĄ - po prostu NIE twórz tej sekcji w HTML. Bez komunikatów "brak danych", bez pustych sekcji.
Jeżeli nie jest podany tytuł naukowy (np.: licencjat, inżynier, magister) nie domyślaj się, zostaw dane bez tytułu. 

3. Struktura HTML5:
   - Główny kontener: <div class="cv-container">
   - Header: <header class="cv-header">
   - Każda sekcja: <section class="cv-section">
   - Nagłówki sekcji: <h2>
   - Pozycje (doświadczenie/edukacja): <article class="cv-item">

4. Format dla pozycji doświadczenia/edukacji:
   <article class="cv-item">
     <h3>Stanowisko — Firma</h3>
     <p class="meta">Lokalizacja | Data od — Data do</p>
     <ul>
       <li>Osiągnięcie 1</li>
       <li>Osiągnięcie 2</li>
     </ul>
   </article>

5. Header z danymi kontaktowymi:
   <header class="cv-header">
     <h1>Imię Nazwisko</h1>
     <div class="contact">
       <span>email@example.com</span>
       <span>+48 123 456 789</span>
       <span>Miasto</span>
     </div>
   </header>

6. Techniczne wymagania:
   - Dokument: <!DOCTYPE html>
   - <head>:
     * <meta charset="UTF-8">
     * <meta name="viewport" content="width=device-width, initial-scale=1.0">
     * <title>CV - [Imię Nazwisko]</title>
     * <style></style> (pusty tag - style dodane później)
   - Proste, semantyczne tagi HTML5
   - Minimalne klasy CSS (tylko do identyfikacji elementów)

7. KRYTYCZNE:
   - Używaj WYŁĄCZNIE danych od użytkownika
   - NIE dodawaj placeholder'ów ani przykładowych danych
   - NIE twórz sekcji bez rzeczywistych danych
   - NIE piszesz "Brak danych" ani podobnych komunikatów
   - Jeśli użytkownik nie podał np. lokalizacji - po prostu jej nie umieszczaj

OUTPUT:
Zwróć TYLKO gotowy dokument HTML z danymi użytkownika.
Bez żadnych wyjaśnień przed ani po kodzie.
Na końcu (przed </body>) dodaj komentarz identyfikujący utworzone sekcje:
<!-- Sekcje: header, [lista_utworzonych_sekcji] -->
'''

generate_cv_structure_prompt = ChatPromptTemplate.from_messages(
  [
    ("system", system),
    ("human", 'Dane do CV: \n\n{accepted_cv_data}')
  ]
)

generate_cv_structure_chain = generate_cv_structure_prompt | get_llm() |StrOutputParser()