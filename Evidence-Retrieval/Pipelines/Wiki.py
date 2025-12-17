# pipelines/wiki.py

import re
import requests
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize
from nltk.util import ngrams
from fuzzywuzzy import fuzz


# ==============================
# 🔹 PREPROCESSING + SEMANTIC EXPANSION
# ==============================
def preprocess_and_expand(query: str):
    query = query.lower()
    query = re.sub(r"[^a-zA-Z0-9\s]", "", query)

    tokens = word_tokenize(query)
    stop_words = set(stopwords.words("english"))
    tokens = [t for t in tokens if t not in stop_words]

    # n-grams
    bigrams = [" ".join(bg) for bg in ngrams(tokens, 2)]
    trigrams = [" ".join(tg) for tg in ngrams(tokens, 3)]

    # WordNet synonym expansion
    synonyms = set()
    for token in tokens:
        for syn in wordnet.synsets(token):
            for lemma in syn.lemmas():
                name = lemma.name().replace("_", " ")
                if name.isalpha() and name not in stop_words:
                    synonyms.add(name)

    expanded = list(set(tokens + bigrams + trigrams + list(synonyms)))
    return expanded


# ==============================
# 🔹 WIKIPEDIA SEARCH FUNCTIONS
# ==============================
HEADERS = {
    "User-Agent": "Evidence-Retrieval/1.0 (academic-research)"
}


def search_wikipedia(query, limit=5):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "srlimit": limit,
    }

    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json().get("query", {}).get("search", [])
    except requests.exceptions.RequestException as e:
        print(f"❌ Wikipedia search failed for '{query}': {e}")
        return []


def get_page_summary(title):
    url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + title.replace(" ", "_")
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Summary request failed for '{title}': {e}")
        return None


# ==============================
# 🔹 MAIN WIKIPEDIA PIPELINE
# ==============================
def wiki_pipeline(user_query, limit=5):
    """
    Input  : user_query (str)
    Output : List[dict] with unified schema
    """
    expanded_queries = preprocess_and_expand(user_query)

    all_results = []
    seen_titles = set()

    # prioritize longer (more specific) queries
    expanded_queries.sort(key=lambda x: len(x.split()), reverse=True)

    for q in expanded_queries[:10]:
        results = search_wikipedia(q, limit)
        for r in results:
            title = r.get("title")
            if title and title not in seen_titles:
                seen_titles.add(title)
                all_results.append(r)

    # fuzzy filtering
    filtered_results = [
        r for r in all_results
        if fuzz.partial_ratio(user_query.lower(), r["title"].lower()) > 60
    ]

    final_results = []
    doc_counter = 0

    for r in filtered_results[:limit]:
        summary = get_page_summary(r["title"])
        if not summary:
            continue

        doc_counter += 1
        final_results.append({
            "doc_id": f"wiki_{doc_counter}",
            "source": "wikipedia",
            "title": r["title"],
            "url": summary.get("content_urls", {})
                           .get("desktop", {})
                           .get("page", ""),
            "text": summary.get("extract", "")
        })

    return final_results
