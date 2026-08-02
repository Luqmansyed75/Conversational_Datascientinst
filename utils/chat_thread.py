import uuid
import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

POSTGRES_URL = os.getenv("POSTGRES_URL")


def generate_thread_id() -> str:
    """Generate a unique thread ID for a new conversation."""
    return str(uuid.uuid4())


def parse_message(msg) -> tuple[str, str]:
    """
    Extract (role, content) from a message structure.
    Handles both dictionaries and LangChain message objects safely.
    """
    if isinstance(msg, dict):
        role = msg.get("role")
        if not role:
            msg_type = msg.get("type")
            role = "user" if msg_type == "human" else "assistant"
        content = msg.get("content", "")
        return role, content
    else:
        msg_type = getattr(msg, "type", "human")
        role = "user" if msg_type == "human" else "assistant"
        content = getattr(msg, "content", "")
        return role, content


def get_thread_history(app, thread_id: str) -> list[dict]:
    """
    Fetch chat_history for a thread from the Postgres LangGraph checkpoint.
    Returns a list of {role, content} dicts ready for the API response.

    Args:
        app       : the compiled LangGraph app (passed in to avoid circular imports)
        thread_id : the thread whose history to fetch
    """
    config   = {"configurable": {"thread_id": thread_id}}
    snapshot = app.get_state(config)

    if not snapshot or not snapshot.values:
        return []

    messages = snapshot.values.get("chat_history", [])
    result   = []
    for msg in messages:
        role, content = parse_message(msg)
        result.append({"role": role, "content": content})
    return result


def clear_thread(thread_id: str) -> dict:
    """
    Delete ALL checkpoint data for a given thread_id from Postgres.
    Clears from all three tables created by PostgresSaver.setup().
    """
    conn = psycopg.connect(POSTGRES_URL, autocommit=True)
    try:
        with conn.cursor() as cur:
            for table in ["checkpoints", "checkpoint_writes", "checkpoint_blobs"]:
                cur.execute(
                    f"DELETE FROM {table} WHERE thread_id = %s",
                    (thread_id,)
                )
    finally:
        conn.close()
    return {"message": f"Thread '{thread_id}' deleted successfully."}


def list_threads(app) -> list[dict]:
    """
    Return all threads stored in Postgres, with their title (first user message).
    Queries the checkpoints table for distinct thread_ids, then reads the
    LangGraph checkpoint state to extract the first human message as the title.

    Args:
        app : the compiled LangGraph app (passed in to avoid circular imports)
    """
    conn = psycopg.connect(POSTGRES_URL, autocommit=True)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT thread_id FROM checkpoints")
            thread_ids = [row[0] for row in cur.fetchall()]
    finally:
        conn.close()

    threads = []
    for thread_id in thread_ids:
        config   = {"configurable": {"thread_id": thread_id}}
        snapshot = app.get_state(config)
        history  = snapshot.values.get("chat_history", []) if snapshot and snapshot.values else []
        
        # Use the first human message content as the conversation title
        title = "New Conversation"
        for msg in history:
            role, content = parse_message(msg)
            if role == "user":
                title = content[:40]
                break
        threads.append({"thread_id": thread_id, "title": title})

    return threads

