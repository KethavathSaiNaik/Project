from datetime import datetime
from uuid import uuid4
import os
import json
from app.explainability_chatbot import build_explainability_index
from Pipelines.nltk_setup import setup_nltk
from Pipelines.Wiki import wiki_pipeline
from Pipelines.Scholar import scholar_pipeline
from Pipelines.Gnews import gnews_pipeline
from Pipelines.sentence_splitter import (
    setup_sentence_tokenizer,
    split_documents_into_sentences,
    save_sentences_to_json
)
from app.output_cleanup import cleanup_old_queries
from Retrieval.bm25_retriever import run_bm25
from Retrieval.faiss_retriever import run_faiss
from Retrieval.fusion_and_ranking import run_fusion
from Inference.deberta_nli import run_deberta_nli
from dotenv import load_dotenv

load_dotenv()

# 🚨 Run ONCE when server starts
setup_nltk()
setup_sentence_tokenizer()


# =================================================
# 🔹 SAVE DOCUMENTS
# =================================================
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


# =================================================
# 🔹 MAIN PIPELINE
# =================================================
def verify_claim_pipeline(query_text: str):
    print("\n" + "=" * 90)
    print("🧪 NEW CLAIM VERIFICATION REQUEST")
    print(f"📝 Claim: {query_text}")

    query_id = f"q_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:6]}"
    print(f"🆔 Query ID: {query_id}")

    all_docs = []

    # ---------------- Wikipedia ----------------
    print("\n🚀 Wikipedia pipeline...")
    wiki_docs = wiki_pipeline(query_text, limit=10)
    print(f"   ✔ Retrieved {len(wiki_docs)} documents")
    all_docs.extend(wiki_docs)

    # ---------------- Scholar ------------------
    print("\n🚀 Scholar pipeline...")
    scholar_docs = scholar_pipeline(query_text, limit=10)
    print(f"   ✔ Retrieved {len(scholar_docs)} documents")
    all_docs.extend(scholar_docs)

    # ---------------- GNews --------------------
    print("\n🚀 GNews pipeline...")
    GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
    gnews_docs = gnews_pipeline(query_text, GNEWS_API_KEY, limit=10)
    print(f"   ✔ Retrieved {len(gnews_docs)} documents")
    all_docs.extend(gnews_docs)

    print(f"\n📦 Total documents collected: {len(all_docs)}")

    # Attach query_id to documents
    for doc in all_docs:
        doc["query_id"] = query_id

    # Save documents (RESTORED STEP)
    save_docs_to_json(all_docs, query_id, query_text)

    # ---------------- Sentence Splitting ----------------
    print("\n✂️ Splitting documents into sentences...")
    sentences = split_documents_into_sentences(all_docs)
    print(f"   ✔ Total sentences generated: {len(sentences)}")
    save_sentences_to_json(sentences, query_id)

    # ---------------- Retrieval -------------------------
    print("\n🔍 Running BM25 retriever...")
    run_bm25(query_id, query_text)

    print("\n🧠 Running FAISS retriever...")
    run_faiss(query_id, query_text)

    print("\n⚖️ Running fusion & ranking...")
    run_fusion(query_id, alpha=0.6, top_k=5)

    # ---------------- NLI -------------------------------
    print("\n🧠 Running DeBERTa NLI (multi-evidence single-shot)...")
    nli_result = run_deberta_nli(
        query_id=query_id,
        claim=query_text,
        top_k=5
    )
    build_explainability_index(query_id, top_k=5)
    if nli_result is None:
        print("❌ NLI failed — no result returned")
        return {
            "query_id": query_id,
            "claim": query_text,
            "error": "NLI inference failed"
        }

    # ---------------- Load sentence metadata ----------------
    sentences_path = f"outputs/sentences/sentences_{query_id}.json"
    with open(sentences_path, "r", encoding="utf-8") as f:
        sentence_data = json.load(f)

    sentence_lookup = {
        s["sentence_id"]: s
        for s in sentence_data["sentences"]
    }

    # ---------------- Enrich Evidence ----------------
    enriched_evidence = []
    for ev in nli_result["evidences"]:
        sid = ev["sentence_id"]
        meta = sentence_lookup.get(sid)

        if meta:
            enriched_evidence.append({
                "sentence_id": sid,
                "sentence_text": meta["sentence_text"],
                "document_id": meta["doc_id"],   # ✅ FIXED
                "source": meta.get("source"),
                "title": meta.get("title"),
                "url": meta.get("url")
            })

    # ---------------- Final Logs ----------------
    print("\n📊 FINAL VERIFICATION RESULT")
    print(f"   🏷 Label      : {nli_result['label']}")
    print(f"   📈 Confidence : {nli_result.get('confidence')}")
    print("=" * 90 + "\n")
    cleanup_old_queries()
    # ---------------- API RESPONSE ----------------
    return {
        "query_id": query_id,
        "claim": query_text,
        "label": nli_result["label"],
        "confidence": nli_result.get("confidence"),
        "evidence": enriched_evidence
    }
