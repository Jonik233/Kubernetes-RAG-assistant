from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import BackgroundTasks

from app.rag.rag import create_assistant
from app.evaluation.online_judge import evaluate_relevance
from app.database.db_save import save_conversation, save_feedback


app = FastAPI()
assistant = create_assistant()

class QueryPayload(BaseModel):
    query: str


@app.post("/query")
def predict(payload: QueryPayload, background_tasks: BackgroundTasks):
    user_input = payload.query
    answer, call_record = assistant.rag(user_input)

    # Offloading evaluations and database writes to background tasks
    background_tasks.add_task(process_telemetry, user_input, answer, call_record)

    return {"Response": answer}


def process_telemetry(user_input, answer, record):
    conversation_id = save_conversation(record, user_input)
    relevance, explanation = evaluate_relevance(user_input, answer)
    save_feedback(conversation_id, "judge", relevance=relevance, explanation=explanation)