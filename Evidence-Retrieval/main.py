from Pipelines.nltk_setup import setup_nltk 
from Pipelines.Wiki import wiki_pipeline 
from Pipelines.Scholar import scholar_pipeline 
from Pipelines.Gnews import gnews_pipeline
import os
import json
from datetime import datetime

from dotenv import load_dotenv


load_dotenv() 
def save_docs_to_json(all_docs, query):
    os.makedirs("outputs", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = f"outputs/all_docs_{timestamp}.json"

    data = {
        "query": query,
        "total_docs": len(all_docs),
        "documents": all_docs
    }

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"💾 Documents saved to: {file_path}")


def main():
    # 🔹 One-time global setup
    setup_nltk()

    query = "machine learning models for early cancer detection using gene expression data"
    all_docs = []

    print("🚀 Wikipedia...")
    all_docs.extend(wiki_pipeline(query, limit=10))

    print("🚀 Scholar...")
    all_docs.extend(scholar_pipeline(query, limit=10))

    print("🚀 GNews...")
    GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
    if not GNEWS_API_KEY:
        raise RuntimeError("GNEWS_API_KEY not found")
    all_docs.extend(gnews_pipeline(query, GNEWS_API_KEY, limit=10))

    print(f"\n📦 Total documents collected: {len(all_docs)}")

    # 💾 Save to JSON
    save_docs_to_json(all_docs, query)


if __name__ == "__main__":
    main()
