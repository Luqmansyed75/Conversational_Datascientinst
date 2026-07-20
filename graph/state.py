from typing import TypedDict, Optional, Annotated
import operator


class AgentState(TypedDict):
    question:       str
    intent:         Optional[str]
    intent_history: list
    rag_context:    Optional[dict]
    sql_data:       Optional[dict]
    final_answer:   Optional[str]
    chat_history:   list
    iteration:      int