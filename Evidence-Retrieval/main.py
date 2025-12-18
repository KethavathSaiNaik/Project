from Pipelines.nltk_setup import setup_nltk
from Pipelines.Wiki import wiki_pipeline
from Pipelines.Scholar import scholar_pipeline
from Pipelines.Gnews import gnews_pipeline
from Pipelines.sentence_splitter import (
    setup_sentence_tokenizer,
    split_documents_into_sentences,
    save_sentences_to_json
)

from Retrieval.bm25_retriever import run_bm25
from Retrieval.faiss_retriever import run_faiss
from Retrieval.fusion_and_ranking import run_fusion

import os
import json
from datetime import datetime
from uuid import uuid4
from dotenv import load_dotenv

load_dotenv()


def save_docs_to_json(all_docs, query_id, query_text):
    os.makedirs("outputs/documents", exist_ok=True)

    file_path = f"outputs/documents/documents_{query_id}.json"

    data = {
        "query_id": query_id,
        "query_text": query_text,
        "total_docs": len(all_docs),
        "documents": all_docs
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"💾 Documents saved to: {file_path}")


def main():
    setup_nltk()
    setup_sentence_tokenizer()

    query_text = "AI techniques can identify tumors early by analyzing genomic expression patterns"
    query_id = f"q_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:6]}"

    all_docs = []

    print("🚀 Wikipedia...")
    all_docs.extend(wiki_pipeline(query_text, limit=10))

    print("🚀 Scholar...")
    all_docs.extend(scholar_pipeline(query_text, limit=10))

    print("🚀 GNews...")
    GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
    if not GNEWS_API_KEY:
        raise RuntimeError("GNEWS_API_KEY not found")
    all_docs.extend(gnews_pipeline(query_text, GNEWS_API_KEY, limit=10))

    for doc in all_docs:
        doc["query_id"] = query_id

    print(f"\n📦 Total documents collected: {len(all_docs)}")

    save_docs_to_json(all_docs, query_id, query_text)

    sentences = split_documents_into_sentences(all_docs)
    save_sentences_to_json(sentences, query_id)

    print("🔍 Running BM25...")
    run_bm25(query_id, query_text)

    print("🧠 Running FAISS...")
    run_faiss(query_id, query_text)

    print("⚖️ Running fusion & ranking...")
    run_fusion(query_id, alpha=0.6, top_k=5)


if __name__ == "__main__":
    main()
