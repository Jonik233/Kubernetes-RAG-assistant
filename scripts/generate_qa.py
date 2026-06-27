"""
This module is used to generate synthetic data for offline evaluation
"""

import os
import json
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel
from app.rag.rag import load_docs
from app.core.config import QA_GEN_INSTRUCTIONS
from concurrent.futures import ThreadPoolExecutor
from app.evaluation.eval_utils import llm_structured_retry, map_progress

load_dotenv()


class Questions(BaseModel):
    questions: list[str]


docs = load_docs()
openai_client = OpenAI()


def generate_ground_truth(document):
    user_prompt = json.dumps(document)

    out, usage = llm_structured_retry(
        openai_client,
        QA_GEN_INSTRUCTIONS,
        user_prompt,
        Questions
    )

    results = []

    for q in out.questions:
        results.append({
            "question": q,
            "document": document["id"]
        })

    return results, usage



with ThreadPoolExecutor(max_workers=6) as pool:
    results = map_progress(pool, docs[:1000], generate_ground_truth)


ground_truth = []
usages = []

for records, usage in results:
    ground_truth.extend(records)
    usages.append(usage)

print(len(ground_truth))


df_ground_truth = pd.DataFrame(ground_truth)
df_ground_truth.to_csv(os.environ["QA_DATA_PATH"], index=False)