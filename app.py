# Entry point — will be built in Phase 6
from fastapi import FastAPI
from api.routes.chat_route import router

app = FastAPI(
    title="Conversational Data Scientist",
    description="Ask questions about your data in natural language.",
    version="1.0.0",
)

app.include_router(router)


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}