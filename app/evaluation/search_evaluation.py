import os
import numpy as np
import pandas as pd
from tqdm.auto import tqdm
from dotenv import load_dotenv
from app.rag.rag_utils import load_docs, build_index

load_dotenv()


def text_search(query):

    return index.search(
        query,
        num_results=10
    )


def compute_relevance(q, search_function):
    doc_id = q["document"]
    results = search_function(query=q["question"])

    relevance = []
    for d in results:
        relevance.append(int(d["id"] == doc_id))

    return relevance


def compute_total_relevance(ground_truth, search_function):
    relevance_total = []

    for q in tqdm(ground_truth):
        relevance = compute_relevance(q, search_function)
        relevance_total.append(relevance)

    return relevance_total


def hit_rate_fn(relevance):
    relevance_matrix = np.array(relevance)
    hit_rate = relevance_matrix.sum() / relevance_matrix.shape[0]
    return hit_rate.item()


def mrr(relevance):
    relevance_matrix = np.array(relevance)
    ranks = np.argmax(relevance_matrix, axis=1)

    score = np.array([1 / (rank + 1) if relevance_matrix[i, rank] != 0 else 0
                      for i, rank in enumerate(ranks)]).sum().item()

    return score / relevance_matrix.shape[0]


def run_search_evaluation(ground_truth, search_function):
    total_relevance = compute_total_relevance(ground_truth, search_function)

    return {
        "hit_rate": hit_rate_fn(total_relevance),
        "mrr": mrr(total_relevance),
    }


if __name__ == "__main__":

    df_ground_truth = pd.read_csv(os.environ["QA_DATA_PATH"])
    ground_truth = df_ground_truth.to_dict(orient="records")

    documents = load_docs()
    index = build_index(documents)

    metrics = run_search_evaluation(ground_truth, text_search)

    print(metrics)