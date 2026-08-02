from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    question:     str
    thread_id:    str
    chat_history: Optional[list] = []


class ChatResponse(BaseModel):
    answer:         Optional[str]
    needs_chart:    Optional[bool]
    has_chart:      bool
    chart_figure:   Optional[str] = None   # Plotly JSON string (fig.to_json())
    intent_history: list


# ── Thread History ────────────────────────────────────────────────────────────
class MessageItem(BaseModel):
    role:    str    # "user" or "assistant"
    content: str


class ThreadHistoryResponse(BaseModel):
    thread_id: str
    messages:  list[MessageItem]


# ── Thread Deletion ───────────────────────────────────────────────────────────
class DeleteThreadResponse(BaseModel):
    message: str