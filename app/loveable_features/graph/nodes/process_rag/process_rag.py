from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.loveable_features.graph.state import State
from app.loveable_features.graph.nodes.process_rag.retriever_openai_embed import get_retriever
from app.config import get_openai
from app.loveable_features.graph.nodes.process_rag.prompt import INSIGHT_PROMPT

retriever = get_retriever()
llm = get_openai()


async def process_rag(state: State) -> State:
    query = state["lead_judge"].devdocs_query
    if not query:
        return {
            "rag_insight": None
        }
    context = retriever.search(query)
    prompt = ChatPromptTemplate.from_messages(
        [
            ('system', INSIGHT_PROMPT),
            ('human', f"""
                Question: {query}.
                Documentation: {context}
                """)
        ]
    )
    chain = prompt | llm | StrOutputParser()
    try:
        response = await chain.ainvoke({})
        credits = state["credits"]
        return {
            "rag_insight": response,
            "credits": credits + 1
        }
    except:
        return {
            "rag_insight": None
        }