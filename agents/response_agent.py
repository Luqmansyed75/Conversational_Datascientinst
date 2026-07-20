import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL  = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

SYSTEM_PROMPT = """You are a friendly and professional company assistant.
Your job is to convert raw data or answers into clear, natural, human-friendly responses.

Rules:
- Always respond in a warm, professional tone
- If given a list of data or table results, summarize them in plain English
- Highlight the most important insight first
- Never expose raw SQL queries to the user
- Keep responses concise but complete
- If the input is already a clean answer, polish it slightly and return it"""


def generate_response(question: str, source: str, data) -> str:
    """
    Args:
        question : original user question
        source   : "rag", "sql", or "general"
        data     : str (rag/general answer) or dict {"sql": ..., "results": [...]} for sql
    """

    if source == "sql":
        sql     = data.get("sql", "")
        results = data.get("results", [])
        user_content = f"""The user asked: {question}
        The database returned these results:{results}Convert this into a clear, friendly natural language response."""

    elif source == "rag":
        user_content = f"""The user asked: {question}
        The retrieved answer is:{data["context"]}
        Polish this into a clear, friendly response."""
        
    elif source == "both":
        rag_ctx  = data["rag_context"]["context"]
        sql_rows = data["sql_data"]["results"]
        user_content = f"""The user asked: {question}
                        SQL Data:{sql_rows}
                        Document Context:{rag_ctx}
                        Combine both sources into a single, clear, friendly response."""

    else:  # general
        user_content = f"""The user asked: {question}

Answer this directly in a friendly, helpful way."""

    response = client.chat.completions.create(
        model    = MODEL,
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_content},
        ],
        temperature = 0.3,
    )

    return response.choices[0].message.content.strip()


if __name__ == "__main__":
    # Test RAG response
    # print("\n--- RAG ---")
    # print(generate_response(
    #     question = "What is the return policy?",
    #     source   = "rag",
    #     data     = "Returns accepted within 30 days with proof of purchase. Products must be in original condition."
    # ))

    # Test SQL response
    print("\n--- SQL ---")
    print(generate_response(
        question = "Top 3 selling products",
        source   = "sql",
        data     = {
            "sql": "SELECT product_name, SUM(quantity) FROM ...",
            "results": [
                {"product_name": "Laptop Pro 14", "total": 245},
                {"product_name": "Wireless Mouse", "total": 183},
                {"product_name": "Headphones X1",  "total": 141},
            ]
        }
    ))

    # Test General response
    print("\n--- General ---")
    print(generate_response(
        question = "What is today's date?",
        source   = "general",
        data     = None
    ))