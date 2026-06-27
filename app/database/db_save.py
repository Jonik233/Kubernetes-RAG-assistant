from datetime import datetime
from app.database.db_init import DB_TIMEZONE
from app.database.db_pool import get_db_connection


def save_feedback(conversation_id, source, relevance=None, explanation=None, score=None):
    timestamp = datetime.now(DB_TIMEZONE)

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO feedback (
                    conversation_id, source, relevance, explanation, score, timestamp
                ) VALUES (
                    %s, %s, %s, %s, %s, %s
                )
                """,
                (conversation_id, source, relevance, explanation, score, timestamp)
            )


def save_conversation(record, question):
    timestamp = datetime.now(DB_TIMEZONE)

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO conversations (
                    question, answer, model, prompt,
                    prompt_tokens, completion_tokens, total_tokens,
                    response_time, cost, timestamp
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                RETURNING id
                """,
                (
                    question,
                    record.answer,
                    record.model,
                    record.prompt,
                    record.prompt_tokens,
                    record.completion_tokens,
                    record.total_tokens,
                    record.response_time,
                    record.cost,
                    timestamp,
                ),
            )
            conversation_id = cur.fetchone()[0]
            return conversation_id