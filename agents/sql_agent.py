# sql_agent.py — SQL Agent
# Will be implemented in Phase 4
import os
import sqlite3
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client  = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL   = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
DB_PATH = os.getenv("DB_PATH", "data/cleaned_data.db")

SYSTEM_PROMPT = """You are an expert SQL query generation agent.

Your objective is to generate accurate, safe, and executable SQL queries based only on the provided database schema.

Strictly follow these rules:

1. Use ONLY the tables and columns present in the provided schema.
2. Never invent or assume table names, column names, relationships, or values.
3. Read the schema carefully before generating any SQL.
4. If the user's request cannot be answered using the provided schema, explain why instead of guessing.
5. Generate syntactically correct SQL for the target database dialect.
6. Use explicit JOIN conditions whenever multiple tables are involved.
7. Prefer INNER JOIN unless the question clearly requires LEFT/RIGHT/FULL joins.
8. Always qualify ambiguous column names with table aliases.
9. Use meaningful table aliases for readability.
10. Never use SELECT * unless the user explicitly requests every column.
11. Select only the columns necessary to answer the question.
12. Apply appropriate WHERE conditions whenever filters are implied by the user's request.
13. Use ORDER BY whenever the question asks for highest, lowest, newest, oldest, top, bottom, first, or last.
14. Use GROUP BY only when aggregate functions are required.
15. Use HAVING only for filtering aggregated results.
16. Use LIMIT (or the database equivalent) when the user requests only a few records.
17. Correctly handle NULL values using IS NULL or IS NOT NULL.
18. Never compare NULL using '=' or '!='.
19. Prefer parameter placeholders instead of embedding user input directly whenever applicable.
20. Never generate destructive SQL statements.

Forbidden statements include:
- DROP, DELETE, UPDATE, INSERT, ALTER, TRUNCATE, CREATE, REPLACE, MERGE

21. Never execute multiple SQL statements in one response.
22. Never include explanations inside the SQL query.
23. Return only one SQL query unless explicitly requested otherwise.
24. If the request is ambiguous, ask a clarification question instead of making assumptions.
25. If multiple interpretations are possible, explain the ambiguity before generating SQL.
26. Preserve exact table and column names from the schema.
27. Do not rename tables or columns unless using SQL aliases.
28. Prefer readable and efficient SQL over unnecessarily complex queries.
29. Avoid nested subqueries when a JOIN or CTE provides a clearer solution.
30. Ensure every generated query is executable without modification.
31. When the user's question is a follow-up or references previously mentioned items (e.g., 'these products', 'show these in a chart', 'for them'), examine the conversation history carefully. Filter the SQL query specifically for those exact items using WHERE (e.g., WHERE product_name IN (...)) or apply the exact LIMIT N from the previous context. Never select the entire table when follow-up items are referenced."""


def get_schema() -> str:
    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]

    schema = []
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        cols = cursor.fetchall()
        col_defs = ", ".join(f"{col[1]} ({col[2]})" for col in cols)
        schema.append(f"Table: {table}\nColumns: {col_defs}")

    conn.close()
    return "\n\n".join(schema)


def generate_sql(question: str, schema: str, chat_history: list = []) -> str:
    # Build conversation messages: system + history + current question
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Inject last 4 messages of chat history for context (e.g. "these products")
    for msg in chat_history[-4:]:
        role = "user" if msg.type == "human" else "assistant"
        messages.append({"role": role, "content": msg.content})

    # Current question with schema
    messages.append({"role": "user", "content": f"Schema:\n{schema}\n\nQuestion: {question}\n\nSQL:"})

    response = client.chat.completions.create(
        model       = MODEL,
        messages    = messages,
        temperature = 0,
    )
    raw = response.choices[0].message.content.strip()

    # Extract only the SQL — strip markdown code blocks if present
    if "```" in raw:
        raw = raw.split("```")[1]
        raw = raw.lstrip("sql").strip()

    return raw


def execute_sql(sql: str) -> list[dict]:
    conn   = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(sql)
    cols    = [desc[0] for desc in cursor.description]
    rows    = cursor.fetchall()
    conn.close()
    return [dict(zip(cols, row)) for row in rows]


def run_sql_agent(question: str, chat_history: list = []) -> dict:
    schema  = get_schema()
    sql     = generate_sql(question, schema, chat_history)
    results = execute_sql(sql)
    return {"sql": sql, "results": results}


if __name__ == "__main__":
    tests = [
        "Show top 5 products by total quantity sold",
        # "Which city has the most customers?",
        # "Average review score per product category",
    ]

    for q in tests:
        print(f"\nQ: {q}")
        output = run_sql_agent(q)
        print(f"SQL: {output['sql']}")
        print(f"Results ({len(output['results'])} rows):")
        for row in output["results"][:5]:
            print(f"  {row}")
        print("-" * 50)