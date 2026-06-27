from pydantic import BaseModel
from contextlib import asynccontextmanager
from fastapi import FastAPI, BackgroundTasks

from app.rag.rag import create_assistant
from app.database.db_pool import init_pool, pool
from app.evaluation.online_judge import evaluate_relevance
from app.database.db_save import save_conversation, save_feedback


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler
    """

    # Initialize and open the connection pool
    db_pool = init_pool()
    db_pool.open()
    print("Database connection pool opened successfully.")

    # Loading RAG assistant
    app.state.assistant = create_assistant()

    yield

    # Close all connections in the pool cleanly
    if pool:
        pool.close()
        print("Database connection pool closed safely.")

    # Deleting assistant
    del app.state.assistant



app = FastAPI(lifespan=lifespan)

class QueryPayload(BaseModel):
    query: str


@app.post("/query")
def predict(payload: QueryPayload, background_tasks: BackgroundTasks):
    user_input = payload.query
    answer, call_record = app.state.assistant.rag(user_input)

    # Offloading evaluations and database writes to background tasks
    background_tasks.add_task(process_telemetry, user_input, answer, call_record)

    return {"Response": answer}


def process_telemetry(user_input, answer, record):
    conversation_id = save_conversation(record, user_input)
    relevance, explanation = evaluate_relevance(user_input, answer)
    save_feedback(conversation_id, "judge", relevance=relevance, explanation=explanation)