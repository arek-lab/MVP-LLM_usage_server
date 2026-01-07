from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.graph.chains.cv_data_model import CVData
from app.config import OPENAI_API_KEY, GPT_MODEL

def get_llm():
    return ChatOpenAI(
        api_key=OPENAI_API_KEY,
        model=GPT_MODEL,
        temperature=0,
    )
structured_llm = get_llm().with_structured_output(CVData)

system = """Jesteś expertem w obróbce danych z otrzymanych od kandydatów CV. Jesteś znany z dokładności i adekwatności. Twoje dane są zawsze zgodne z otrzymanym materiałem, nigdy nie wymyślasz danych.
Twoim zadaniem jest zapoznanie się z otrzymanymi informacjami, wynikiem porównania cv z ofertą oraz feedbackiem od użytkownika. Dokonaj ewentualnego mergu danych w przypadku, gdy feedback jest zgodny z oczekiwaniem wyniku porównania cv z ofertą. Jeżeli feedback zawiera informacje o skończonych kursach lub znajomości języków obcych dodaj te dane obligatoryjnie. Zwróć we wskazanej strukturze.
"""

human = '''Inforamcje do przetworzenia:
Dane z CV:\n {extracted_cv}.\n
Wynik porównania CV z ofertą:\n {comparison_result} \n
Feedback od użytkownika: \n {additional_info_human_feedback}
'''

collect_prompt = ChatPromptTemplate.from_messages(
  [
    ("system", system),
    ("human", human)
  ]
)

collect_all_data_chain = collect_prompt | structured_llm