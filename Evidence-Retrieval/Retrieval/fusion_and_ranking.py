import os
import json
import numpy as np


def load_bm25_scores(query_id):
    path = f"outputs/bm25/bm25_scores_{query_id}.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["scores"]


def load_faiss_scores(query_id):
    path = f"outputs/faiss/faiss_scores_{query_id}.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["scores"]


def load_sentences(query_id):
    path = f"outputs/sentences/sentences_{query_id}.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {s["sentence_id"]: s for s in data["sentences"]}


def min_max_normalize(values):
    min_v = min(values)
    max_v = max(values)
    if max_v - min_v == 0:
        return [0.0 for _ in values]
    return [(v - min_v) / (max_v - min_v) for v in values]


def fuse_and_rank(query_id, alpha=0.6, top_k=10):
    bm25_scores = load_bm25_scores(query_id)
    faiss_scores = load_faiss_scores(query_id)
    sentences = load_sentences(query_id)

    bm25_map = {s["sentence_id"]: s["bm25_score"] for s in bm25_scores}
    faiss_map = {s["sentence_id"]: s["faiss_score"] for s in faiss_scores}

    sentence_ids = list(bm25_map.keys())

    bm25_values = [bm25_map[sid] for sid in sentence_ids]
    faiss_values = [faiss_map.get(sid, 0.0) for sid in sentence_ids]

    bm25_norm = min_max_normalize(bm25_values)
    faiss_norm = min_max_normalize(faiss_values)

    fused = []

    for sid, x, y in zip(sentence_ids, bm25_norm, faiss_norm):
        final_score = alpha * x + (1 - alpha) * y
        sent = sentences[sid]

        fused.append({
            "query_id": query_id,
            "sentence_id": sid,
            "final_score": float(final_score),
            "bm25_score": bm25_map[sid],
            "faiss_score": faiss_map.get(sid, 0.0),
            "sentence_text": sent["sentence_text"],
            "doc_id": sent["doc_id"],
            "source": sent["source"],
            "title": sent["title"],
            "url": sent["url"]
        })

    fused.sort(key=lambda x: x["final_score"], reverse=True)
    return fused[:top_k]


def save_fused_results(results, query_id):
    os.makedirs("outputs/fusion", exist_ok=True)

    path = f"outputs/fusion/final_ranked_sentences_{query_id}.json"

    with open(path, "w", encoding="utf-8") as f:
        json.dump({
            "query_id": query_id,
            "total_results": len(results),
            "results": results
        }, f, indent=2, ensure_ascii=False)

    print(f"💾 Final ranked evidence saved to: {path}")


def run_fusion(query_id, alpha=0.6, top_k=10):
    results = fuse_and_rank(query_id, alpha=alpha, top_k=top_k)
    save_fused_results(results, query_id)
    return results
