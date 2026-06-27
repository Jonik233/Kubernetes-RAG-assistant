from pydantic import BaseModel
from typing import Literal
from openai import OpenAI

from app.evaluation.eval_utils import llm_structured_retry
from app.core.config import ONLINE_JUDGE_INSTRUCTIONS, ONLINE_JUDGE_PROMPT


class RelevanceVerdict(BaseModel):
    relevance: Literal["NON_RELEVANT", "PARTLY_RELEVANT", "RELEVANT"]
    explanation: str


def evaluate_relevance(question, answer, client=None):
    if client is None:
        client = OpenAI()

    prompt = ONLINE_JUDGE_PROMPT.format(
        question=question,
        answer=answer
    )

    result, usage = llm_structured_retry(
        client,
        ONLINE_JUDGE_INSTRUCTIONS,
        prompt,
        RelevanceVerdict,
    )

    return result.relevance, result.explanation