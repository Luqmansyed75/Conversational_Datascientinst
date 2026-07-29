from fastapi import APIRouter
from api.schemas.chat_schema import ChatRequest, ChatResponse
from graph.graph import run
from utils.chat_thread import generate_thread_id

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/new-thread")
def new_thread():
    """Create a new conversation thread and return its ID."""
    thread_id = generate_thread_id()
    return {"thread_id": thread_id}


@router.post("/ask", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    result = run(
        question=payload.question,
        thread_id=payload.thread_id,
        chat_history=payload.chat_history,
    )
    return ChatResponse(
        answer=result["answer"],
        needs_chart=result["needs_chart"],
        has_chart=result["chart_figure"] is not None,
        intent_history=result["intent_history"],
    )