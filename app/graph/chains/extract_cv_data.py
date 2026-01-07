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

llm = get_llm().with_structured_output(
    CVData
)

system = """Jesteś expertem w obróbce danych z otrzymanych od kandydatów CV. Jesteś znany z dokładności i adekwatności. Twoje dane są zawsze zgodne z otrzymanym materiałem, nigdy nie wymyślasz danych."""

extract_prompt = ChatPromptTemplate.from_messages(
    [("system", system), ("human", "Wyciągnij dane z poniższego CV:\n\n{cv_text}")]
)

extract_chain = extract_prompt | llm
