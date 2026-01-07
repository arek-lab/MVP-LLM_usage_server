from app.graph.state import State
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from langchain_tavily import TavilySearch, TavilyExtract
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
import os
import copy
from app.graph.chains.job_description_model import JobDescription

tavily_search = TavilySearch(max_result=3)
tavily_search = TavilySearch(max_results=3)
tavily_extract = TavilyExtract(
    extract_depth="basic", 
    include_images=False,
    format="text"
)

@tool
def load_web_page(url: str) -> str:
    """Tool to extract data from web page"""
    try:
        # 1: Tavily Extract
        result = tavily_extract.invoke({"urls": [url]})
        if result and 'results' in result and result['results']:
            content = result['results'][0].get('raw_content', '')
            if content:
                return content
        
        # 2: Fallback cloudscraper
        import cloudscraper
        from bs4 import BeautifulSoup
        
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        for tag in soup(['script', 'style', 'nav', 'footer']):
            tag.decompose()
        
        return soup.get_text(separator='\n', strip=True)
        
    except Exception as e:
        return f"Error: {str(e)}"


tools = [tavily_search, load_web_page]

llm = ChatOpenAI(model=os.getenv("GPT_MODEL"))
llm_with_tools = llm.bind_tools(tools=tools)
llm_structured = llm.with_structured_output(JobDescription)

system = """Jesteś expertem w przygotowywaniu analitycznych opisów stanowisk dla ofert pracy. Jeżeli masz link do oferty korzystasz z narzędzia "load_web_page". Jeżeli masz tylko nazwę stanowiska, korzystasz z narzędzia wyszukiwania "tavily_search". Finalnie zwracasz analityczny opis stanowiska."""


async def search_job_description(state: State) -> State:
    messages = [SystemMessage(content=system)] + state["job_offer_agent_messages"]

    # Sprawdź czy ostatnia wiadomość to ToolMessage (wynik wykonania narzędzia)
    last_message = (
        state["job_offer_agent_messages"][-1]
        if state["job_offer_agent_messages"]
        else None
    )

    if isinstance(last_message, ToolMessage):
        # structured output
        conversation_summary = "\n".join(
            [
                msg.content
                for msg in state["job_offer_agent_messages"]
                if hasattr(msg, "content")
                and isinstance(msg.content, str)
                and msg.content
            ]
        )

        structured_prompt = f"""Na podstawie poniższych informacji przygotuj strukturalny opis stanowiska:

{conversation_summary}.

Wyodrębnij kluczowe informacje i uporządkuj je w przejrzystej strukturze."""

        result = await llm_structured.ainvoke(
            [SystemMessage(content=structured_prompt)]
        )

        job_offer_description = result
        # add info aimaeesage
        job_offer_agent_messages = state["job_offer_agent_messages"] + [
            AIMessage(content="Structured output generated")
        ]
        return {
            "job_offer_agent_messages": job_offer_agent_messages,
            "job_offer_description": result,
        }
    else:
        # tool action
        result = await llm_with_tools.ainvoke(messages)

        job_offer_agent_messages = state["job_offer_agent_messages"] + [result]
        return {
            "job_offer_agent_messages": job_offer_agent_messages,
        }


tool_node = ToolNode(tools, messages_key="job_offer_agent_messages")
