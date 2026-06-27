import re
import hashlib
from typing import List, Dict, Any


def clean_and_split_sentences(text: str) -> List[str]:
    """
    Advanced technical text splitter that protects common technical abbreviations
    and code block boundaries from naive punctuation splitting.
    """
    # Protect common abbreviations by temporarily masking periods
    protected = text
    protected = re.sub(r'\b(e\.g\.|i\.e\.|vs\.)', lambda m: m.group(1).replace('.', '___'), protected)
    protected = re.sub(r'\b(apps/v1\.|core/v1\.)', lambda m: m.group(1).replace('.', '___'), protected)

    # Split sentences on true sentence terminators
    raw_sentences = re.split(r'(?<=[.!?])\s+', protected)

    # Unmask the periods inside the isolated sentences
    sentences = [s.replace('___', '.') for s in raw_sentences if s.strip()]
    return sentences


def build_production_docs(doc: Dict[str, Any], target_sentence_count: int = 5) -> List[Dict[str, Any]]:
    """
    Builds chunks based on a provided document
    """
    sentences = clean_and_split_sentences(doc["content"])
    chunks = []

    for i in range(0, len(sentences), target_sentence_count):
        chunk_text = " ".join(sentences[i:i + target_sentence_count]).strip()
        if len(chunk_text) > 50:
            chunks.append(chunk_text)

    docs = []
    total_chunks = len(chunks)

    for idx, chunk in enumerate(chunks):
        # Generate a deterministic parent ID using an MD5 hash of the URL
        url_hash = hashlib.md5(doc["url"].encode('utf-8')).hexdigest()[:12]
        parent_id = f"doc_{url_hash}"

        # Unique chunk ID built deterministically using the positional index
        chunk_id = f"{parent_id}_c{idx:03d}"

        doc_item = {
            "id": chunk_id,
            "text": chunk,
            "metadata": {
                "source_url": doc["url"],
                "page_title": doc["title"],
                "chunk_index": idx,
                "total_chunks": total_chunks,
                "prev_chunk_id": f"{parent_id}_c{(idx - 1):03d}" if idx > 0 else None,
                "next_chunk_id": f"{parent_id}_c{(idx + 1):03d}" if idx < (total_chunks - 1) else None
            }
        }
        docs.append(doc_item)

    return docs