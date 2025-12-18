import os
import json
import nltk


def setup_sentence_tokenizer():
    nltk.download("punkt", quiet=True)


def split_documents_into_sentences(documents):
    sentences = []

    for doc in documents:
        query_id = doc["query_id"]
        doc_id = doc["doc_id"]

        try:
            doc_sents = nltk.sent_tokenize(doc["text"])
        except Exception:
            continue

        for idx, sent in enumerate(doc_sents):
            sent = sent.strip()
            if not sent:
                continue

            sentences.append({
                "query_id": query_id,
                "sentence_id": f"s_{doc_id}_{idx}",
                "doc_id": doc_id,
                "source": doc["source"],
                "title": doc["title"],
                "url": doc["url"],
                "sentence_index": idx,
                "sentence_text": sent
            })

    return sentences


def save_sentences_to_json(sentences, query_id):
    os.makedirs("outputs/sentences", exist_ok=True)

    path = f"outputs/sentences/sentences_{query_id}.json"

    with open(path, "w", encoding="utf-8") as f:
        json.dump({
            "query_id": query_id,
            "total_sentences": len(sentences),
            "sentences": sentences
        }, f, indent=2, ensure_ascii=False)

    print(f"💾 Sentences saved to: {path}")
