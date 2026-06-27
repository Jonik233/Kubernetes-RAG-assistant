import os
from dotenv import load_dotenv
from contextlib import contextmanager
from psycopg_pool import ConnectionPool

load_dotenv()


DB_CONN_INFO = (
    f"host={os.getenv('DB_HOST', 'localhost')} "
    f"dbname={os.getenv('DB_NAME', 'rag-database')} "
    f"user={os.getenv('DB_USER', 'user')} "
    f"port={os.getenv('DB_PORT', '5432')} "
    f"password={os.getenv('DB_PASSWORD', 'password')}"
)

# Global pool variable
pool = None


def init_pool():
    global pool
    if pool is None:
        pool = ConnectionPool(
            conninfo=DB_CONN_INFO,
            min_size=2,  # Minimum number of permanent idle connections
            max_size=10,  # Maximum number of concurrent connections
            open=False  # Don't open connections until .open() is called explicitly
        )
    return pool


@contextmanager
def get_db_connection():
    """
    Context manager to borrow a connection from the pool and automatically
    return it when done, even if exceptions occur.
    """
    if pool is None:
        raise RuntimeWarning("Database pool is not initialized. Call init_pool() first.")

    with pool.connection() as conn:
        yield conn