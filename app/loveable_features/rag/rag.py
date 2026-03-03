import asyncio
from pydantic import BaseModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app.loveable_features.graph.nodes.process_rag.retriever_openai_embed import get_retriever
from app.config import get_openai
from app.loveable_features.rag.prompt import RAG_PROMPT, TRANSLATE_PROMPT

llm = get_openai()

class Translation(BaseModel):
    english_query: str
    original_language: str

translation_llm = llm.with_structured_output(Translation)

translation_chain = ChatPromptTemplate.from_messages([
    ("system", TRANSLATE_PROMPT),
    ("human", "{query}")
]) | translation_llm


async def rag_query(query: str) -> str | None:
    translation = await translation_chain.ainvoke({"query": query})
    english_query = translation.english_query
    original_language = translation.original_language
    retriever = get_retriever()
    context = await asyncio.to_thread(retriever.search, english_query)
    prompt = ChatPromptTemplate.from_messages([
        ('system', RAG_PROMPT),
        ('human', f"Question: {query}.\nOriginal language: {original_language}\nRelevant excerpts from Lovable documentation:\n{context}")
    ], template_format="mustache")
    
    chain = prompt | llm | StrOutputParser()
    try:
        return await chain.ainvoke({})
    except:
        return "LLM generation Error"