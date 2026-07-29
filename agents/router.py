import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL  = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

ROUTER_PROMPT = """You are an intent classifier for a company chatbot.
Classify the user's question as "rag", "sql", or "general".

Return "sql" if the question is about:
- Sales, revenue, quantities, counts, customers, orders, products, rankings

Return "rag" if the question is about:
- Company policies, employee handbook, office timings, FAQs, product descriptions

Return "general" if the question is generic or conversational.

Reply with ONLY one word: rag, sql, or general.

Question: {question}
"""
SUFFICIENCY_PROMPT = """You are evaluating whether enough data has been collected to answer a user's question.

Question: {question}

Data collected so far:
SQL Results : {sql_data}
RAG Context : {rag_context}
    
Rules:
1.compare the data present with the query and If you think the present data is sufficient to answer the question, reply "ready".
2. If SQL Results contains the data needed AND RAG Context contains the document details needed (or if all needed info is present), reply "ready".
3. If RAG Context is missing or empty, but document info (policy, warranty, terms) is needed, reply "needs_rag".
4. If SQL Results is missing or empty, but database info (sales, counts, customers) is needed, reply "needs_sql".


Reply with ONLY one word: ready, needs_sql, or needs_rag. No extra text.
"""

def route(question: str) -> str:
    response = client.chat.completions.create(
        model       = MODEL,
        messages    = [{"role": "user", "content": ROUTER_PROMPT.format(question=question)}],
        temperature = 0,
        max_tokens  = 5,
    )
    intent = response.choices[0].message.content.strip().lower()
    return intent if intent in ("rag", "sql", "general") else "rag"


def check_sufficiency(question: str, sql_data, rag_context) -> str:
    # Truncate to preview only — check_sufficiency only needs to know IF data exists
    sql_preview = str(sql_data)[:300] + "..." if sql_data and len(str(sql_data)) > 300 else str(sql_data or "None")
    rag_preview = str(rag_context)[:300] + "..." if rag_context and len(str(rag_context)) > 300 else str(rag_context or "None")

    response = client.chat.completions.create(
        model       = MODEL,
        messages    = [{"role": "user", "content": SUFFICIENCY_PROMPT.format(
            question    = question,
            sql_data    = sql_preview,
            rag_context = rag_preview,
        )}],
        temperature = 0,
        max_tokens  = 10,
    )
    result = response.choices[0].message.content.strip().lower()
    return result if result in ("ready", "needs_sql", "needs_rag") else "ready"