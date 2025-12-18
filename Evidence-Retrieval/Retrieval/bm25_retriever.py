import json
import os
import nltk
from rank_bm25 import BM25Okapi


def load_sentences(query_id):
    path = f"outputs/sentences/sentences_{query_id}.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["sentences"]


def tokenize(text):
    return [t.lower() for t in nltk.word_tokenize(text)]


def compute_bm25_scores(query_text, sentences):
    corpus = [tokenize(s["sentence_text"]) for s in sentences]
    bm25 = BM25Okapi(corpus)

    query_tokens = tokenize(query_text)
    scores = bm25.get_scores(query_tokens)

    results = []
    for sent, score in zip(sentences, scores):
        results.append({
            "query_id": sent["query_id"],
            "sentence_id": sent["sentence_id"],
            "bm25_score": float(score)
        })

    return results


def save_bm25_scores(results, query_id):
    os.makedirs("outputs/bm25", exist_ok=True)

    path = f"outputs/bm25/bm25_scores_{query_id}.json"

    with open(path, "w", encoding="utf-8") as f:
        json.dump({
            "query_id": query_id,
            "total_sentences": len(results),
            "scores": results
        }, f, indent=2)

    print(f"💾 BM25 scores saved to: {path}")


def run_bm25(query_id, query_text):
    sentences = load_sentences(query_id)
    results = compute_bm25_scores(query_text, sentences)
    save_bm25_scores(results, query_id)
    return results
