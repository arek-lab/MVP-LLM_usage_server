from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from app.config import OPENAI_API_KEY, GPT_MODEL
from app.text_crafter.chains.simplify_flow.prompts import SYSTEM_PROMPT, get_simplify_prompt
from app.text_crafter.chains.model import LLMResponseModel

def get_llm():
    return ChatOpenAI(model=GPT_MODEL, api_key=OPENAI_API_KEY)


llm = get_llm().with_structured_output(LLMResponseModel)


def get_simplify_chain(
    subcategory: str,
    content: str,
    target_audience: str = None,
    preserve_meaning: bool = False
):
    """
    Tworzy chain do skracania tekstu.
    
    Args:
        subcategory: Typ skracania (brief_summary, remove_fluff, key_points, executive_summary)
        content: Tekst do skrócenia
        target_length: Docelowa długość ("very_short", "short", "medium") - opcjonalne
        preserve_tone: Czy zachować ton oryginalnego tekstu
    
    Returns:
        Runnable chain z structured output (LLMResponseModel)
    """
    user_prompt = get_simplify_prompt(
        subcategory=subcategory,
        content=content,
        target_audience=target_audience,
        preserve_meaning=preserve_meaning
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", user_prompt)
    ])
    
    chain = prompt | llm
    
    return chain