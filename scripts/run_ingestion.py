"""
This module is used to pre-process scraped docs and create production ready chunked documents
"""

import os
import json
from tqdm.auto import tqdm

from dotenv import load_dotenv
load_dotenv()

from ingestion.scraper import crawl
from scripts.doc_builder import build_production_docs


def run(in_memory_load=False):
    if in_memory_load:
        docs = []

        with open(os.environ["RAW_DATA_PATH"], "r") as f:
            for doc in f:
                docs.append(json.loads(doc))
    else:
        docs = crawl(num_pages=70)

        with open(os.environ["RAW_DATA_PATH"], "w") as f:
            for item in tqdm(docs, total=len(docs), desc="Downloading raw docs in storage"):
                f.write(json.dumps(item) + "\n")

    docs_chunks = []

    for doc in tqdm(docs, total=len(docs), desc="Chunking raw docs"):
        chunks = build_production_docs(doc)
        docs_chunks.extend(chunks)

    with open(os.environ["CHUNKED_DATA_PATH"], "w") as f:
        for item in tqdm(docs_chunks, total=len(docs_chunks), desc="Downloading chunks into storage"):
            f.write(json.dumps(item) + "\n")

    print(f"Generated {len(docs_chunks)} docs' chunks")


if __name__ == "__main__":
    run(in_memory_load=True)