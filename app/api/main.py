from fastapi import FastAPI
from pydantic import BaseModel

from app.rag.rag import create_assistant
from app.evaluation.online_judge import evaluate_relevance
from deployment.db_save import save_conversation, save_feedback


app = FastAPI()
assistant = create_assistant()

class QueryPayload(BaseModel):
    query: str

@app.post("/query")
def predict(payload: QueryPayload):
    user_input = payload.query
    answer = assistant.rag(user_input)

    # Saving conversation
    record = assistant.last_call
    conversation_id = save_conversation(record, user_input)

    # Evaluating the relevance of rag answer
    relevance, explanation = evaluate_relevance(user_input, answer)

    # Saving relevance score
    save_feedback(conversation_id, "judge",
                  relevance=relevance, explanation=explanation)

    return {"Response": answer}