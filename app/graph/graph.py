from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AIMessage
from app.graph.state import State
from app.graph.nodes.extract_cv_node import extract_cv_node
from app.graph.nodes.search_job_description_agent import search_job_description, tool_node
from app.graph.nodes.compare_cv_to_offer import compare_cv_to_offer
from app.graph.nodes.human_review import human_review
from app.graph.nodes.collect_all_cv_data import collect_all_cv_data
from app.graph.nodes.generate_cv_structure import generate_cv_structure
from app.graph.nodes.add_style_and_optimize import add_style_and_optimize
# from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool
import os
import logging

logger = logging.getLogger(__name__)


# checkpointer = MemorySaver()
checkpointer = None
db_pool = None

async def init_checkpointer():
    """Initialize PostgreSQL checkpointer"""
    global checkpointer, db_pool
    try:
        # Create connection pool
        db_pool = AsyncConnectionPool(
            conninfo=os.getenv("DATABASE_URL"),
            min_size=1,
            max_size=10
        )
        
        # Create checkpointer with pool
        checkpointer = AsyncPostgresSaver(db_pool)
        await checkpointer.setup()  # Creates tables
        
        logger.info("PostgreSQL checkpointer initialized")
        return checkpointer
    except Exception as e:
        logger.error(f"Failed to initialize checkpointer: {e}")
        raise

async def close_checkpointer():
    """Close checkpointer connection pool"""
    global db_pool
    if db_pool:
        await db_pool.close()
        logger.info("PostgreSQL connection pool closed")



flow = StateGraph(State)


def should_continue(state: State) -> str:
    last_message = state["job_offer_agent_messages"][-1]

    if (
        isinstance(last_message, AIMessage)
        and hasattr(last_message, "tool_calls")
        and last_message.tool_calls
    ):
        return "tools"
    else:
        return "compare_cv_to_offer"


flow.add_node(
    "extract_cv", extract_cv_node, metadata={"label": "Wyciągam dane z CV..."}
)
flow.add_node(
    "job_description",
    search_job_description,
    metadata={"label": "Opracowuję opis oferty pracy lub stanowiska..."},
)
flow.add_node("tools", tool_node, metadata={"label": "Korzystam z internetu..."})
flow.add_node(
    "compare_cv_to_offer",
    compare_cv_to_offer,
    metadata={"label": "Porównuję dane z CV z ofertą pracy lub stanowiskiem..."},
)
flow.add_node(
    "human review",
    human_review,
    metadata={
        "label": "Oczekuje na dodatkowe informacje lub potwierdzenie kontynuacji..."
    },
)
flow.add_node("collect all data",
              collect_all_cv_data,
              metadata={"label": "Zbieram i przetwarzam dostepne informacje..."})
flow.add_node("generate cv structure", generate_cv_structure,
              metadata={"label": "Generuję strukturę CV w HTML...."})
flow.add_node("add style and optymize", add_style_and_optimize, metadata={"label": "Dodaję style i generuję PDF"})

flow.add_edge(START, "extract_cv")
flow.add_edge("extract_cv", "job_description")
flow.add_conditional_edges(
    "job_description",
    should_continue,
    {"tools": "tools", "compare_cv_to_offer": "compare_cv_to_offer"},
)
flow.add_edge("tools", "job_description")
flow.add_edge("compare_cv_to_offer", "human review")
flow.add_edge("human review", "collect all data")
flow.add_edge("collect all data", "generate cv structure")
flow.add_edge("generate cv structure", "add style and optymize")
flow.add_edge("add style and optymize", END)

graph = flow.compile(checkpointer=checkpointer)
# graph.get_graph().draw_mermaid_png(output_file_path="graph.png")
