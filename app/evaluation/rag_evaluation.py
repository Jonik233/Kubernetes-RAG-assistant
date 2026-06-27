import os
import pandas as pd
from openai import OpenAI
from typing import Literal
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from concurrent.futures import ThreadPoolExecutor
from app.core.config import AQA_JUDGE_INSTRUCTIONS, AQA_JUDGE_PROMPT
from app.evaluation.eval_utils import calc_total_price, llm_structured_retry, map_progress

load_dotenv()



class AnswerEvaluation(BaseModel):
    reasoning: str = Field(
        description="Reasoning about the quality of the answer."
    )
    score: Literal["good", "bad"] = Field(
        description="'good' if the answer is correct and complete, 'bad' otherwise."
    )


def evaluate_llm_answer(question, answer_orig, answer_llm, model="gpt-4o-mini", llm_client=OpenAI()):
    prompt = AQA_JUDGE_PROMPT.format(
        question=question,
        answer_orig=answer_orig,
        answer_llm=answer_llm
    )

    result, usage = llm_structured_retry(
        llm_client,
        AQA_JUDGE_INSTRUCTIONS,
        prompt,
        AnswerEvaluation,
        model=model
    )

    return result, usage



def judge_record(rec):
    eval_result, usage = evaluate_llm_answer(
        question=rec["question"],
        answer_orig=rec["answer_orig"],
        answer_llm=rec["answer_llm"]
    )

    result = {
        "question": rec["question"],
        "document": rec["document"],
        "score": eval_result.score,
        "reasoning": eval_result.reasoning,
    }

    return result, usage



if __name__ == "__main__":
    df_answers = pd.read_csv(os.environ["GENERATED_ANSWERS_TO_QA"])
    answers = df_answers.to_dict(orient="records")

    with ThreadPoolExecutor(max_workers=6) as pool:
        results = map_progress(pool, answers[:600], judge_record)

    evaluations = []
    usages = []

    for evaluation, usage in results:
        evaluations.append(evaluation)
        usages.append(usage)

    df_eval = pd.DataFrame(evaluations)
    print(df_eval.head())
    print("-" * 100 + "\n")

    print(df_eval.score.value_counts(normalize=True))

    print(f"Evaluation price: {calc_total_price(usages)}")

    df_eval.to_csv(os.environ["RAG_EVAL_PATH"], index=False)