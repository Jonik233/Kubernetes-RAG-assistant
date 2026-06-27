import os
import time
import pandas as pd
from tqdm.auto import tqdm
from concurrent.futures import ThreadPoolExecutor



def calc_price(usage):
    input_price_per_million = 0.75
    output_price_per_million = 4.50

    input_cost = (usage.input_tokens / 1_000_000) * input_price_per_million
    output_cost = (usage.output_tokens / 1_000_000) * output_price_per_million
    total_cost = input_cost + output_cost

    return {
        "input_cost": input_cost,
        "output_cost": output_cost,
        "total_cost": total_cost,
    }


def calc_total_price(usages):
    total_cost = 0.0

    for usage in usages:
        cost = calc_price(usage)
        total_cost = total_cost + cost["total_cost"]

    return total_cost


def llm_structured(client, instructions, user_prompt, output_type, model="gpt-4o-mini"):
    messages = [
        {"role": "developer", "content": instructions},
        {"role": "user", "content": user_prompt}
    ]

    response = client.responses.parse(
        model=model,
        input=messages,
        text_format=output_type
    )

    return response.output_parsed, response.usage


def llm_structured_retry(
    client,
    instructions,
    user_prompt,
    output_type,
    model="gpt-4o-mini",
    max_retries=3,
):
    for attempt in range(max_retries):
        try:
            return llm_structured(
                client,
                instructions,
                user_prompt,
                output_type,
                model=model,
            )
        except Exception:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)


def map_progress(pool, seq, f):
    results = []

    with tqdm(total=len(seq)) as progress:
        futures = []

        for el in seq:
            future = pool.submit(f, el)
            future.add_done_callback(lambda p: progress.update())
            futures.append(future)

        for future in futures:
            result = future.result()
            results.append(result)

    return results


def generate_rag_answer(assistant, record, idx_to_doc):
    question = record["question"]
    doc_id = record["document"]
    original_doc = idx_to_doc[doc_id]

    llm_answer = assistant.rag(question)
    answer_orig = original_doc["text"]

    result = {
        "question": question,
        "answer_llm": llm_answer,
        "answer_orig": answer_orig,
        "document": doc_id,
    }

    return result


def gen_and_load_rag_answers(assistant, ground_truth_data, idx_to_doc):
    assistant.reset_usage()

    gen_rag_answer_fn = lambda record: generate_rag_answer(record=record, assistant=assistant, idx_to_doc=idx_to_doc)

    with ThreadPoolExecutor(max_workers=6) as pool:
        results = map_progress(pool, ground_truth_data, gen_rag_answer_fn)

    df_answers = pd.DataFrame(results)
    df_answers.to_csv(os.environ["GENERATED_ANSWERS_TO_QA"], index=False)

    return assistant.total_cost()

