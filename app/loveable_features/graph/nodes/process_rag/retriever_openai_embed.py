"""
Retriever for Lovable docs Pinecone index.

Usage:
    from retriever import Retriever

    r = Retriever(pinecone_api_key="...", openai_api_key="...")
    context = r.search("how to connect Supabase")
    # przekaż context do LLM jako kontekst
"""

# import logging

from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone
from app.config import OPENAI_API_KEY, PINECONE_API_KEY

# logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

DEFAULT_INDEX_NAME   = "lovable-docs"
DEFAULT_EMBED_MODEL  = "text-embedding-3-small"
DEFAULT_RERANK_MODEL = "BAAI/bge-reranker-base"


# ---------------------------------------------------------------------------
# Retriever
# ---------------------------------------------------------------------------

class Retriever:
    """
    Wyszukiwarka semantyczna po Pinecone index z opcjonalnym rerankerem.

    Parameters
    ----------
    pinecone_api_key : Pinecone API key (pobierz z https://app.pinecone.io)
    openai_api_key   : OpenAI API key; jeśli None — pobiera z env OPENAI_API_KEY
    index_name       : nazwa indeksu Pinecone (musi zgadzać się z index_docs.py)
    embed_model      : model embeddingów OpenAI (musi być ten sam co przy indeksowaniu!)
    rerank_model     : CrossEncoder do rerankingu — None wyłącza reranking
    candidates_k     : ile kandydatów pobrać z Pinecone przed rerankiem
    final_k          : ile wyników zwrócić po reranku
    score_threshold  : minimalny rerank score (0.0–1.0); None = brak filtrowania
    """

    def __init__(
        self,
        pinecone_api_key: str | None = None,
        openai_api_key:   str | None   = None,
        index_name:       str          = DEFAULT_INDEX_NAME,
        embed_model:      str          = DEFAULT_EMBED_MODEL,
        rerank_model:     str | None   = DEFAULT_RERANK_MODEL,
        candidates_k:     int          = 10,
        final_k:          int          = 5,
        score_threshold:  float | None = 0.3,
    ):
        self.candidates_k    = candidates_k
        self.final_k         = final_k
        self.score_threshold = score_threshold

        # Sprawdź czy indeks istnieje
        pc = Pinecone(api_key=pinecone_api_key)
        existing = [idx.name for idx in pc.list_indexes()]
        if index_name not in existing:
            raise ValueError(
                f"Pinecone index '{index_name}' not found. Available: {existing}"
            )

        oai_key = OPENAI_API_KEY
        if not oai_key:
            raise EnvironmentError("OpenAI API key not provided and OPENAI_API_KEY env var not set.")

        # logger.info("Loading embedding model: %s", embed_model)
        embeddings = OpenAIEmbeddings(
            model=embed_model,
            openai_api_key=oai_key,
        )

        # logger.info("Connecting to Pinecone index: %s", index_name)
        self.vectorstore = PineconeVectorStore(
            index_name=index_name,
            embedding=embeddings,
            pinecone_api_key=PINECONE_API_KEY,
        )

        self.pc       = pc
        self.reranker = rerank_model is not None

        # logger.info("Retriever ready.")

    # ------------------------------------------------------------------
    # Publiczne API
    # ------------------------------------------------------------------

    def search(self, query: str) -> str:
        """
        Wyszukaj najbardziej trafne fragmenty dokumentacji dla podanego zapytania.

        Zwraca gotowy string do wklejenia jako kontekst dla LLM.
        Format:
            [1] URL: https://...
            ---
            <treść chunka>

            [2] ...
        """
        chunks = self._retrieve(query)
        if not chunks:
            return "Nie znaleziono pasujących fragmentów dokumentacji."
        return self._format_for_llm(chunks)

    def search_raw(self, query: str) -> list[dict]:
        """
        Jak search(), ale zwraca listę słowników zamiast stringa.
        Przydatne gdy chcesz samodzielnie formatować kontekst.

        Każdy element:
            {
                "url":     str,
                "content": str,
            }
        """
        chunks = self._retrieve(query)
        return [
            {
                "url":     c.metadata.get("source", ""),
                "content": c.page_content,
            }
            for c in chunks
        ]

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _retrieve(self, query: str):
        """Pobierz kandydatów z Pinecone, opcjonalnie zreankuj."""
        candidates = self.vectorstore.similarity_search(query, k=self.candidates_k)

        if not candidates:
            return []

        if self.reranker is None:
            return candidates[:self.final_k]

        return self._rerank(query, candidates)

    def _rerank(self, query: str, candidates):
        docs_text = [doc.page_content for doc in candidates]
        
        results = self.pc.inference.rerank(
            model="bge-reranker-v2-m3",
            query=query,
            documents=docs_text,
            top_n=self.final_k,
            return_documents=True,
        )
        
        # Filtruj po score_threshold jeśli ustawiony
        reranked = []
        for r in results.data:
            if self.score_threshold is None or r.score >= self.score_threshold:
                reranked.append(candidates[r.index])
        
        return reranked

    @staticmethod
    def _format_for_llm(chunks) -> str:
        parts = []
        for i, chunk in enumerate(chunks, 1):
            url = chunk.metadata.get("source", "")
            parts.append(f"[{i}] URL: {url}\n---\n{chunk.page_content}")
        return "\n\n".join(parts)

# lazy initailization
_retriever: Retriever | None = None

def get_retriever() -> Retriever:
    global _retriever
    if _retriever is None:
        _retriever = Retriever(
            score_threshold=0.3,
            final_k=5,
        )
    return _retriever


# ---------------------------------------------------------------------------
# Szybki test z CLI: python retriever.py "twoje zapytanie" --pinecone-key "klucz"
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    from dotenv import load_dotenv
    load_dotenv()

    # logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    parser = argparse.ArgumentParser()
    parser.add_argument("query", nargs="*", default=["how to connect Supabase to Lovable"])
    parser.add_argument("--pinecone-key", required=True, help="Pinecone API key")
    parser.add_argument("--openai-key",   default=None,  help="OpenAI API key (lub ustaw OPENAI_API_KEY)")
    parser.add_argument("--index-name",   default=DEFAULT_INDEX_NAME)
    args = parser.parse_args()

    r = Retriever(
        pinecone_api_key=args.pinecone_key,
        openai_api_key=args.openai_key,
        index_name=args.index_name,
    )
    query = " ".join(args.query)
    print("\n" + "=" * 60)
    print(f"Query: {query}")
    print("=" * 60 + "\n")
    print(r.search(query))