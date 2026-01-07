from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import List
from app.config import OPENAI_API_KEY, GPT_MODEL


class ComparisonResult(BaseModel):
    matching_information: List[str] = Field(
        description="Informacje z CV, które pasują do oferty"
    )
    irrelevant_information: List[str] = Field(
        description="Rzeczy zbędne / niepotrzebne lub takie, które mogą zaburzać ocenę rekrutera"
    )
    missing_information: List[str] = Field(
        description="dane, których brakuje, a są ważne w ofercie"
    )
    overall_fit_score: int = Field(
        description="ogólne oszacowanie dopasowania CV do oferty w skali 0-10"
    )
    suggested_additions: List[str] = Field(
        description="pytania o umiejętności, doświadczenie, rodzje szkoleń, i inne, które warto dodać do CV, czego brakuje, żeby lepiej pasowało"
    )
    suggested_removals: List[str] = Field(
        description="pytania o zgodę na usunięcie informacji, które można usunąć / uprościć, bo są zbędne"
    )

def get_llm():
    return ChatOpenAI(
        api_key=OPENAI_API_KEY,
        model=GPT_MODEL,
        temperature=0,
    )
structured_llm = get_llm().with_structured_output(ComparisonResult)

system = """Jesteś doświadczonym rekruterem. Twoim zadaniem jest analiza dostarczonych informacji na temat oferty stanowiska pracy oraz danych z CV. Nie wymyślaj informacji, korzystaj tylko z dostepnych danych.
"suggested_additions" skonstruuj jako listę pytań, które należy zadać userowi, żeby doprecyzować / uzupełnić inforamcje z CV.
"suggested_removals" to lista propozycji usunięcia zbędnych, niepotrzebnych informacji. NIe proponuj usunięcia historii zatrudnienia, ponieważ może to wywołać wrażenie luki w zatrudnieniu.
"""

compare_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        (
            "human",
            "Dane z CV: \n{extracted_cv}\n\n Dane na temat oferty: \n{job_offer_description}.",
        ),
    ]
)

compare_chain = compare_prompt | structured_llm
