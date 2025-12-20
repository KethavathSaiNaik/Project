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


# # ==============================
# # 🔹 SEMANTIC SCHOLAR PIPELINE
# # ==============================
# def scholar_pipeline(user_query, limit=5):
#     """
#     Input  : user_query (str)
#     Output : List[dict] with unified schema
#     Source : Semantic Scholar (official API)
#     """

#     url = "https://api.semanticscholar.org/graph/v1/paper/search"

#     params = {
#         "query": user_query,
#         "limit": limit,
#         "fields": "title,abstract,url"
#     }

#     headers = {
#         "User-Agent": "Evidence-Retrieval/1.0 (academic-research)"
#     }

#     try:
#         # polite delay (Semantic Scholar recommends this)
#         time.sleep(1)

#         response = requests.get(
#             url,
#             params=params,
#             headers=headers,
#             timeout=15
#         )
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
#             "source": "semantic_scholar",
#             "title": item.get("title", "N/A"),
#             "url": item.get("url", ""),
#             "text": abstract
#         })

#     return final_results
# ==============================
# 🔹 HYBRID SCHOLAR PIPELINE
#    OpenAlex (Primary) + Semantic Scholar (Fallback)
# ==============================
def scholar_pipeline(user_query, limit=5):
    """
    Input  : user_query (str)
    Output : List[dict] with unified schema
    """

    import requests
    import time
    import os

    final_results = []
    seen_titles = set()
    doc_counter = 0

    # -------------------------------------------------
    # 🔹 1) OPENALEX (PRIMARY)
    # -------------------------------------------------
    try:
        openalex_url = "https://api.openalex.org/works"
        openalex_params = {
            "search": user_query,
            "per-page": limit,
            "filter": "has_abstract:true"
        }

        headers = {
            "User-Agent": "Evidence-Retrieval/1.0 (academic-research)"
        }

        time.sleep(0.3)
        r = requests.get(openalex_url, params=openalex_params, headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json()

        for item in data.get("results", []):
            abstract_inverted = item.get("abstract_inverted_index")
            if not abstract_inverted:
                continue

            # reconstruct abstract
            words = []
            for w, positions in abstract_inverted.items():
                for p in positions:
                    if p >= len(words):
                        words.extend([None] * (p - len(words) + 1))
                    words[p] = w
            abstract_text = " ".join(w for w in words if w)

            title = item.get("title", "").strip().lower()
            if title in seen_titles:
                continue

            seen_titles.add(title)
            doc_counter += 1

            final_results.append({
                "doc_id": f"scholar_{doc_counter}",
                "source": "semantic_scholar OpenAlex",   # keep unchanged
                "title": item.get("title", "N/A"),
                "url": item.get("id", ""),
                "text": abstract_text
            })

    except Exception as e:
        print(f"⚠️ OpenAlex failed: {e}")

    # -------------------------------------------------
    # 🔹 2) SEMANTIC SCHOLAR (FALLBACK)
    # -------------------------------------------------
    if len(final_results) < limit:
        try:
            scholar_url = "https://api.semanticscholar.org/graph/v1/paper/search"
            scholar_params = {
                "query": user_query,
                "limit": limit,
                "fields": "title,abstract,url"
            }

            headers = {
                "User-Agent": "Evidence-Retrieval/1.0",
                "x-api-key": os.getenv("SEMANTIC_SCHOLAR_API_KEY", "")
            }

            retries = 3
            for attempt in range(retries):
                time.sleep(2 ** attempt)
                r = requests.get(scholar_url, params=scholar_params, headers=headers, timeout=15)

                if r.status_code == 200:
                    data = r.json()
                    break
                elif r.status_code == 429:
                    print(f"⏳ Scholar rate limited (retry {attempt+1})")
                    continue
                else:
                    data = {}
                    break

            for item in data.get("data", []):
                abstract = item.get("abstract")
                if not abstract:
                    continue

                title = item.get("title", "").strip().lower()
                if title in seen_titles:
                    continue

                seen_titles.add(title)
                doc_counter += 1

                final_results.append({
                    "doc_id": f"scholar_{doc_counter}",
                    "source": "semantic_scholar SS",
                    "title": item.get("title", "N/A"),
                    "url": item.get("url", ""),
                    "text": abstract
                })

                if len(final_results) >= limit:
                    break

        except Exception as e:
            print(f"⚠️ Semantic Scholar failed: {e}")

    return final_results
