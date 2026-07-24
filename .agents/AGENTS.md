# Project Rules — Conversational Data Scientist

## Stack Preferences

- **Always prefer LangChain and LangGraph components** when building agents, chains, tools, or workflows.
  - Use `langchain_groq.ChatGroq` as the LLM interface — not the raw `groq` client — unless there is a specific reason.
  - Use `@tool` from `langchain_core.tools` for defining tools.
  - Use `create_react_agent` from `langgraph.prebuilt` for agent orchestration — not the deprecated `create_tool_calling_agent` or `AgentExecutor`.
  - Use `llm.with_structured_output(Schema)` for structured extraction.
  - Use `llm.bind_tools([...])` when the LLM needs to decide which tool to call.
  - Use LangGraph `StateGraph` for multi-step agent workflows.

- **Raw `groq` client** may still be used in existing agents (router, sql_agent, rag_agent, response_agent) to avoid refactoring stable code, unless the user requests a rewrite.

## General Rules

- Ask before making significant design decisions.
- Do not over-engineer — keep implementations simple and focused.
- Always install packages inside the `.venv` using `& ".venv\Scripts\python.exe" -m pip install <package>`.
