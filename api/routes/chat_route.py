from fastapi import APIRouter
from api.schemas.chat_schema import (
    ChatRequest, ChatResponse,
    ThreadHistoryResponse, MessageItem, DeleteThreadResponse,
)
from graph.graph import run
from utils.chat_thread import generate_thread_id, get_thread_history, clear_thread, list_threads

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/new-thread")
def new_thread():
    """Create a new conversation thread and return its ID."""
    thread_id = generate_thread_id()
    return {"thread_id": thread_id}


@router.get("/threads")
def get_threads():
    """Return all thread IDs and titles from Postgres."""
    from graph.graph import app
    return {"threads": list_threads(app)}



@router.get("/history/{thread_id}", response_model=ThreadHistoryResponse)
def thread_history(thread_id: str):
    """Fetch full chat history for a thread from the Postgres LangGraph checkpoint."""
    from graph.graph import app          # imported here to avoid circular import at module level
    messages = get_thread_history(app, thread_id)
    return ThreadHistoryResponse(
        thread_id=thread_id,
        messages=[MessageItem(**m) for m in messages],
    )


@router.delete("/thread/{thread_id}", response_model=DeleteThreadResponse)
def delete_thread(thread_id: str):
    """Delete all checkpoint data for a thread from Postgres."""
    return clear_thread(thread_id)


@router.post("/ask", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    result = run(
        question=payload.question,
        thread_id=payload.thread_id,
        chat_history=payload.chat_history,
    )
    return ChatResponse(
        answer         = result["answer"],
        needs_chart    = result["needs_chart"],
        has_chart      = result["chart_figure"] is not None,
        chart_figure   = result["chart_figure"],
        intent_history = result["intent_history"],
    )