import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

PROJECT_ROOT    = Path(__file__).resolve().parent.parent
CHROMA_PATH     = PROJECT_ROOT / os.getenv("CHROMA_PATH", "data/chroma_db")
COLLECTION_NAME = "company_docs"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def load_embedding_model():
    return HuggingFaceEmbeddings(
        model_name   = EMBEDDING_MODEL,
        model_kwargs = {"local_files_only": True},
    )


def load_vector_db(embedding_model):
    return Chroma(
        persist_directory  = str(CHROMA_PATH),
        embedding_function = embedding_model,
        collection_name    = COLLECTION_NAME,
    )


def create_retriever(vector_db):
    return vector_db.as_retriever(
        search_type   = "similarity",
        search_kwargs = {"k": 3},
    )


# cached — model loads once per session
_retriever = None

def retrieve(query: str) -> list[dict]:
    global _retriever

    if _retriever is None:
        embedding_model = load_embedding_model()
        vector_db       = load_vector_db(embedding_model)
        _retriever      = create_retriever(vector_db)

    docs = _retriever.invoke(query)

    return [
        {
            "text":     doc.page_content,
            "source":   doc.metadata.get("source",   "unknown"),
            "page_num": doc.metadata.get("page_num", 0),
        }
        for doc in docs
    ]


if __name__ == "__main__":
    queries = [
        "What is the warranty period for electronics?",
        "How many days does standard delivery take?",

    ]

    for query in queries:
        print(f"\nQuery : {query}")
        for i, r in enumerate(retrieve(query), 1):
            print(f"  [{i}] {r['source']} (p{r['page_num']}) — {r['text'][:80]}...")