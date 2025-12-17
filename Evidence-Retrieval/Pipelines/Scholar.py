# # pipelines/scholar.py

# import requests


# # ==============================
# # 🔹 MAIN SCHOLAR PIPELINE
# # ==============================
# def scholar_pipeline(user_query, limit=5):
#     """
#     Input  : user_query (str)
#     Output : List[Document] with fixed schema
#     """
#     url = "https://api.semanticscholar.org/graph/v1/paper/search"
#     params = {
#         "query": user_query,
#         "limit": limit,
#         "fields": "title,abstract,url"
#     }

#     try:
#         response = requests.get(url, params=params, timeout=10)
#         response.raise_for_status()
#         data = response.json()
#     except requests.exceptions.RequestException as e:
#         print(f"❌ Semantic Scholar API request failed: {e}")
#         return []

#     final_results = []
#     doc_counter = 0

#     for item in data.get("data", []):
#         abstract = item.get("abstract")
#         if not abstract:
#             continue

#         doc_counter += 1
#         final_results.append({
#             "doc_id": f"scholar_{doc_counter}",
#             "source": "scholar",
#             "title": item.get("title", "N/A"),
#             "url": item.get("url", ""),
#             "text": abstract
#         })

#     return final_results
# pipelines/scholar.py

import requests
import time


# ==============================
# 🔹 SEMANTIC SCHOLAR PIPELINE
# ==============================
def scholar_pipeline(user_query, limit=5):
    """
    Input  : user_query (str)
    Output : List[dict] with unified schema
    Source : Semantic Scholar (official API)
    """

    url = "https://api.semanticscholar.org/graph/v1/paper/search"

    params = {
        "query": user_query,
        "limit": limit,
        "fields": "title,abstract,url"
    }

    headers = {
        "User-Agent": "Evidence-Retrieval/1.0 (academic-research)"
    }

    try:
        # polite delay (Semantic Scholar recommends this)
        time.sleep(1)

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=15
        )
        response.raise_for_status()
        data = response.json()

    except requests.exceptions.RequestException as e:
        print(f"❌ Semantic Scholar API request failed: {e}")
        return []

    final_results = []
    doc_counter = 0

    for item in data.get("data", []):
        abstract = item.get("abstract")
        if not abstract:
            continue

        doc_counter += 1
        final_results.append({
            "doc_id": f"scholar_{doc_counter}",
            "source": "semantic_scholar",
            "title": item.get("title", "N/A"),
            "url": item.get("url", ""),
            "text": abstract
        })

    return final_results
