# pipelines/gnews.py

import re
import requests
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.util import ngrams
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer, util


# =============================
# 🔹 MODEL (load once)
# =============================
_model = None


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


# =============================
# 🔹 TEXT PREPROCESSING
# =============================
def preprocess_query(text: str):
    text = text.lower()
    text = re.sub(r"[^a-z\s]", "", text)
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words("english"))
    return [t for t in tokens if t not in stop_words]


# =============================
# 🔹 N-GRAM GENERATION
# =============================
def generate_ngrams(tokens, n):
    return [" ".join(gram) for gram in ngrams(tokens, n)]


# =============================
# 🔹 HYBRID N-GRAM SELECTION
# =============================
def select_relevant_ngrams(query, ngram_list, top_k=5):
    if not ngram_list:
        return []

    model = get_model()

    # Semantic similarity
    emb_query = model.encode(query, convert_to_tensor=True)
    emb_ngrams = model.encode(ngram_list, convert_to_tensor=True)
    semantic_scores = util.cos_sim(emb_query, emb_ngrams)[0].cpu().tolist()

    # TF-IDF
    tfidf = TfidfVectorizer(vocabulary=ngram_list)
    tfidf_scores = tfidf.fit_transform([query]).toarray()[0]

    # Heuristic score
    heuristic_scores = [len(term.split()) / 3 for term in ngram_list]

    combined_scores = [
        0.6 * s + 0.3 * t + 0.1 * h
        for s, t, h in zip(semantic_scores, tfidf_scores, heuristic_scores)
    ]

    ranked = sorted(zip(ngram_list, combined_scores), key=lambda x: -x[1])
    return [t for t, _ in ranked[:top_k]]


# =============================
# 🔹 QUERY EXPANSION
# =============================
def expand_query(user_query, max_length=200):
    tokens = preprocess_query(user_query)
    if not tokens:
        return user_query

    bigrams = generate_ngrams(tokens, 2)
    trigrams = generate_ngrams(tokens, 3)
    candidates = trigrams + bigrams + tokens

    top_terms = select_relevant_ngrams(user_query, candidates, top_k=6)

    main_topic = tokens[0]
    query_parts = []
    current_length = 0

    for term in top_terms:
        connector = " OR " if query_parts else ""
        part = f'{connector}"{term}"'
        if current_length + len(part) > max_length:
            break
        query_parts.append(part)
        current_length += len(part)

    return f'("{main_topic}" AND (' + "".join(query_parts) + "))"


# =============================
# 🔹 MAIN GNEWS PIPELINE
# =============================
def gnews_pipeline(user_query, api_key, limit=20, lang="en"):
    """
    Input  : user_query (str)
    Output : List[dict] with unified schema
    """
    expanded = expand_query(user_query)
    encoded_query = requests.utils.quote(expanded)

    url = (
        f"https://gnews.io/api/v4/search?"
        f"q={encoded_query}"
        f"&lang={lang}"
        f"&max={limit}"
        f"&apikey={api_key}"
    )

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ GNews API request failed: {e}")
        return []

    final_results = []
    doc_counter = 0

    for article in data.get("articles", []):
        description = article.get("description")
        if not description:
            continue

        doc_counter += 1
        final_results.append({
            "doc_id": f"gnews_{doc_counter}",
            "source": "gnews",
            "title": article.get("title", "N/A"),
            "url": article.get("url", ""),
            "text": description
        })

    return final_results
