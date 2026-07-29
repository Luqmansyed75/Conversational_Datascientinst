from typing import TypedDict, Optional, Any, Annotated
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    question:       str
    intent:         Optional[str]
    intent_history: list
    rag_context:    Optional[dict]
    sql_data:       Optional[dict]
    final_answer:   Optional[str]
    needs_chart:    Optional[bool]     # set by response_node
    chart_figure:   Optional[Any]      # set by viz_node — stores go.Figure
    chat_history:   Annotated[list, add_messages]  # reducer: auto-appends, never overwrites
    iteration:      int