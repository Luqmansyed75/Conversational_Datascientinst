import os
from dotenv import load_dotenv
from rag.retriever import retrieve

load_dotenv()


def run_rag_agent(question: str) -> dict:
    chunks = retrieve(question)

    context = "\n\n".join(
        f"[Source: {c['source']} | Page {c['page_num']}]\n{c['text']}"
        for c in chunks
    )

    return {
        "context": context,
        "chunks":  chunks,
    }


if __name__ == "__main__":
    result = run_rag_agent("What is the return policy?")
    print(result["context"])