from datetime import datetime
from dotenv import load_dotenv
from app.database.db_pool import get_db_connection

load_dotenv()


DB_TIMEZONE = datetime.now().astimezone().tzinfo
print(f"Using timezone: {DB_TIMEZONE}")


def init_db(drop=False):

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            if drop:
                cur.execute("DROP TABLE IF EXISTS conversations")

            cur.execute("""
                CREATE TABLE conversations (
                    id SERIAL PRIMARY KEY,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    model TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    prompt_tokens INTEGER NOT NULL,
                    completion_tokens INTEGER NOT NULL,
                    total_tokens INTEGER NOT NULL,
                    response_time FLOAT NOT NULL,
                    cost FLOAT NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
                )
            """)


def init_feedback():
    """
    source: "user" for human feedback, "judge" for LLM evaluations
    score: +1 for thumbs up, -1 for thumbs down
    relevance and explanation: will be used later by the built-in judge
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS feedback")

            cur.execute("""
                CREATE TABLE feedback (
                    id SERIAL PRIMARY KEY,
                    conversation_id INTEGER REFERENCES conversations(id),
                    source TEXT NOT NULL,
                    relevance TEXT,
                    explanation TEXT,
                    score INTEGER,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
                )
            """)