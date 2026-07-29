from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    question: str
    thread_id: str
    chat_history: Optional[list] = []


class ChatResponse(BaseModel):
    answer: Optional[str]
    needs_chart: Optional[bool]
    has_chart: bool
    intent_history: list