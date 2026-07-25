import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel, Field

load_dotenv()

llm = ChatGroq(
    model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
    temperature=0.3,
)

# ── Structured output schema ────────────────────────────────────────────────
class ResponseOutput(BaseModel):
    """LLM returns both the answer and chart decision in one call."""
    answer      : str  = Field(description="Natural language response to the user's question.")
    needs_chart : bool = Field(
        description=(
            "Set True ONLY when BOTH conditions are met: "
            "(1) SQL data is available, AND "
            "(2) EITHER the user explicitly requests a chart/graph/visualization/plot, "
            "OR the question contains trend/comparison language such as: "
            "'show me', 'trend', 'over time', 'monthly', 'yearly', 'daily', "
            "'increased', 'decreased', 'compare', 'last N months', 'per month', "
            "'distribution', 'growth'. "
            "Set False for all other cases — including single values, "
            "RAG-only answers, policy questions, and general questions."
        )
    )


# ── System prompt ───────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a friendly and professional data scientist and company assistant.
Your job is to convert raw data or answers into clear, natural, human-friendly responses.

Rules for generating the answer:
- Always respond in a warm, professional tone.
- Highlight the most important insight first.
- Never expose raw SQL queries to the user.
- Simple Queries (e.g. single factual query, simple count/list): Provide a direct, clean summary.
- Complex Data Queries (e.g. multi-row sales over time, product category breakdowns, performance comparisons):
  1. Provide the direct answer/summary.
  2. Automatically add a section named "📊 Key Insights & Analytics" with deeper analysis:
     - Trends / Growth / Dips (e.g. % increase or decrease, peak/trough periods).
     - Anomalies or key patterns.
     - Practical observations or recommendations.

Examples:

--- Example 1: Simple Query ---
User: "What is the return policy for electronics?"
Data: "Returns accepted within 30 days with receipt."
Answer:
"Electronics can be returned within 30 days of purchase provided you have the original receipt."
needs_chart: False

--- Example 2: Complex Data Query with Analytics ---
User: "Show me monthly sales of Product X for the last 4 months"
Data: [{"month": "May", "sales": 200}, {"month": "June", "sales": 500}, {"month": "July", "sales": 100}, {"month": "August", "sales": 55}]
Answer:
"Here is the monthly sales breakdown for Product X:
- **June**: 500 units
- **May**: 200 units
- **July**: 100 units
- **August**: 55 units

📊 **Key Insights & Analytics**:
- **Peak Performance**: June saw a dramatic +150% surge in sales compared to May, reaching a peak of 500 units.
- **Downward Trend**: Sales dropped sharply by 80% from June to July, continuing to decline into August (55 units).
- **Takeaway**: Investigate potential stock issues or seasonal demand drop-offs post-June."
needs_chart: True

---

Rules for needs_chart (be strict — default is False):
- Set needs_chart=True ONLY when:
    1. The user explicitly asks for a chart, graph, plot, or visualization
    OR
    2. The question contains trend/time-series/comparison language:
       e.g. 'show me', 'trend', 'over time', 'monthly', 'yearly', 'daily',
            'last N months', 'increased', 'decreased', 'compare', 'per month',
            'distribution', 'growth', 'breakdown'
    AND SQL data with multiple rows is available.
- Set needs_chart=False when:
    - The answer is a single value (e.g. 'total revenue is $5000')
    - The question is about policies, FAQs, or documents (RAG)
    - The question is general or conversational
    - No SQL data is available"""


# ── Main entry point ────────────────────────────────────────────────────────
def generate_response(question: str, source: str, data) -> ResponseOutput:
    """
    Args:
        question : original user question
        source   : 'rag', 'sql', 'both', or 'general'
        data     : dict with sql/rag results, or None for general

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

    return structured_llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_content),
    ])


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
    print(f"Answer      :\n{result.answer}")
    print(f"\nNeeds chart : {result.needs_chart}")