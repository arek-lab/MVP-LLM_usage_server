from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from app.config import OPENAI_API_KEY, GPT_MODEL
from app.text_crafter.chains.rewrite_flow.prompts import SYSTEM_PROMPT, get_rewrite_prompt
from app.text_crafter.chains.model import LLMResponseModel


def get_llm():
    return ChatOpenAI(model=GPT_MODEL, api_key=OPENAI_API_KEY)


llm = get_llm().with_structured_output(LLMResponseModel)


def get_rewrite_chain(
    subcategory: str,
    content: str,
    target_audience: str = None,
    target_platform: str = None
):
    """
    Tworzy chain do przepisywania tekstu.
    
    Args:
        subcategory: Typ przepisania (formal_to_informal, improve_clarity, etc.)
        content: Tekst do przepisania
        target_audience: Docelowa grupa odbiorców (opcjonalne)
        target_platform: Docelowa platforma (opcjonalne)
    
    Returns:
        Runnable chain z structured output (RewriteResult)
    """
    user_prompt = get_rewrite_prompt(
        subcategory=subcategory,
        content=content,
        target_audience=target_audience,
        target_platform=target_platform
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", user_prompt)
    ])
    
    chain = prompt | llm
    
    return chain