import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


_model = None


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def load_sentences(query_id):
    path = f"outputs/sentences/sentences_{query_id}.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["sentences"]


def compute_faiss_scores(query_text, sentences):
    model = get_model()

    sentence_texts = [s["sentence_text"] for s in sentences]
    sentence_ids = [s["sentence_id"] for s in sentences]

    embeddings = model.encode(sentence_texts, normalize_embeddings=True)
    embeddings = np.array(embeddings).astype("float32")

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    query_embedding = model.encode(
        [query_text],
        normalize_embeddings=True
    ).astype("float32")

    scores, indices = index.search(query_embedding, len(sentences))
    scores = scores[0]
    indices = indices[0]

    results = []
    for idx, score in zip(indices, scores):
        results.append({
            "query_id": sentences[idx]["query_id"],
            "sentence_id": sentence_ids[idx],
            "faiss_score": float(score)
        })

    return results


def save_faiss_scores(results, query_id):
    os.makedirs("outputs/faiss", exist_ok=True)

    path = f"outputs/faiss/faiss_scores_{query_id}.json"

    with open(path, "w", encoding="utf-8") as f:
        json.dump({
            "query_id": query_id,
            "total_sentences": len(results),
            "scores": results
        }, f, indent=2)

    print(f"💾 FAISS scores saved to: {path}")


def run_faiss(query_id, query_text):
    sentences = load_sentences(query_id)
    results = compute_faiss_scores(query_text, sentences)
    save_faiss_scores(results, query_id)
    return results
