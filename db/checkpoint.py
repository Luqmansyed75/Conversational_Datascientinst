import os
import psycopg
from dotenv import load_dotenv
from langgraph.checkpoint.postgres import PostgresSaver

load_dotenv()

POSTGRES_URL = os.getenv("POSTGRES_URL")

# Create a persistent connection with autocommit (required by PostgresSaver)
conn = psycopg.connect(POSTGRES_URL, autocommit=True)

# Single shared checkpointer instance for the whole app
checkpointer = PostgresSaver(conn)
checkpointer.setup()  # creates the checkpoint tables if they don't exist
