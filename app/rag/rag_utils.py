import os
import json
from minsearch import Index
from dotenv import load_dotenv

load_dotenv()


def load_docs():
    documents = list()
    with open(os.environ["CHUNKED_DATA_PATH"], "r") as f:
        for line in f:
            documents.append(json.loads(line))

    return documents


def build_index(documents):
    index = Index(
        text_fields=['id', 'text', 'page_title']
    )
    index.fit(documents)
    return index
