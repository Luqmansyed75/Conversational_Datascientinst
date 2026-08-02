import os
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from pydantic import BaseModel, Field

load_dotenv()

llm = ChatGroq(
    model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
    temperature=0.3,
)


# ── Structured output schema ────────────────────────────────────────────────
class ResponseOutput(BaseModel):
    """LLM returns both the answer and chart decision in one call."""
    answer      : str  = Field(default="", description="Natural language response to the user's question.")
    needs_chart : bool = Field(default=False, description="Set True ONLY when chart/trend language is present and SQL data is available.")


# ── System prompt ───────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a friendly and professional data scientist and company assistant.
Your job is to convert raw data or answers into clear, natural, human-friendly responses.

Output Requirements:
You must provide a JSON object with two fields:
1. "answer": The natural language markdown string for the user.
2. "needs_chart": A boolean (true or false).

Rules for generating the "answer" string:
- Always respond in a warm, professional tone.
- Highlight the most important insight first.
- Never expose raw SQL queries to the user.
- Do NOT output literal JSON, backticks, or field names like `{"answer": ...}` inside the "answer" text itself.
- Simple Queries (e.g. single factual query, simple count/list): Provide a direct, clean summary.
- Complex Data Queries (e.g. multi-row sales over time, product category breakdowns, performance comparisons):
  1. Provide the direct answer/summary.
  2. Automatically add a section named "📊 Key Insights & Analytics" with deeper analysis:
     - Trends / Growth / Dips (e.g. % increase or decrease, peak/trough periods).
     - Anomalies or key patterns.
     - Practical observations or recommendations.

Rules for "needs_chart":
- Set needs_chart = true ONLY when:
    1. The user explicitly asks for a chart, graph, plot, or visualization
    OR
    2. The question contains trend/time-series/comparison language:
       e.g. 'show me', 'trend', 'over time', 'monthly', 'yearly', 'daily',
            'last N months', 'increased', 'decreased', 'compare', 'per month',
            'distribution', 'growth', 'breakdown'
    AND SQL data with multiple rows is available.
- Set needs_chart = false for all other cases."""


# ── Main entry point ────────────────────────────────────────────────────────
def generate_response(question: str, source: str, data, chat_history: list = []) -> ResponseOutput:
    """
    Args:
        question     : original user question
        source       : 'rag', 'sql', 'both', or 'general'
        data         : dict with sql/rag results, or None for general
        chat_history : list of LangChain message objects (HumanMessage/AIMessage)

    Returns:
        ResponseOutput with 'answer' (str) and 'needs_chart' (bool)
    """
    if source == "sql":
        results = data.get("results", [])
        user_content = (
            f"The user asked: {question}\n"
            f"The database returned these results: {results}\n"
            f"Convert this into a clear, friendly natural language response."
        )

    elif source == "rag":
        user_content = (
            f"The user asked: {question}\n"
            f"The retrieved answer is: {data['context']}\n"
            f"Polish this into a clear, friendly response."
        )

    elif source == "both":
        rag_ctx  = data["rag_context"]["context"]
        sql_rows = data["sql_data"]["results"]
        user_content = (
            f"The user asked: {question}\n"
            f"SQL Data: {sql_rows}\n"
            f"Document Context: {rag_ctx}\n"
            f"Combine both sources into a single, clear, friendly response."
        )

    else:  # general
        user_content = f"The user asked: {question}\nAnswer this directly in a friendly, helpful way."

    structured_llm = llm.with_structured_output(ResponseOutput)

    # Keep only the last 4 messages (2 turns) to stay within Groq's token limit
    MAX_HISTORY = 4
    trimmed_history = chat_history[-MAX_HISTORY:] if len(chat_history) > MAX_HISTORY else chat_history

    res = structured_llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        *trimmed_history,
        HumanMessage(content=user_content),
    ])

    # Clean up any accidental JSON metadata string appended by the LLM inside answer
    if res and res.answer:
        res.answer = re.sub(r'\s*\{"answer".*\}$', '', res.answer, flags=re.DOTALL).strip()
        res.answer = re.sub(r'\s*\{"needs_chart".*\}$', '', res.answer, flags=re.DOTALL).strip()

    return res


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    result = generate_response(
        question = "Top 3 selling products",
        source   = "sql",
        data     = {
            "sql": "SELECT ...",
            "results": [
                {"product_name": "Laptop Pro 14", "total": 245},
                {"product_name": "Wireless Mouse", "total": 183},
                {"product_name": "Headphones X1",  "total": 141},
            ]
        }
    )
    print("Answer      :", result.answer)
    print("Needs chart :", result.needs_chart)