from openai import OpenAI
from dotenv import load_dotenv
from app.rag.rag_utils import load_docs, build_index
from app.rag.rag_base import RAGWithMetrics

load_dotenv()


def create_assistant():
    documents = load_docs()
    index = build_index(documents)
    return RAGWithMetrics(index=index, llm_client=OpenAI())