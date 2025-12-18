# schemas/sentence_schema.py

"""
Sentence Schema

This schema defines the atomic evidence unit used for:
- Sentence splitting
- BM25 retrieval
- FAISS vector search
- DeBERTa NLI inference
- API evidence responses
"""

SENTENCE_SCHEMA = {
    "query_id": "str",          # Links sentence to a specific user query
    "sentence_id": "str",       # Unique sentence ID (e.g., s_wiki_1_0)
    "doc_id": "str",            # Parent document ID
    "source": "str",            # Source: wikipedia | scholar | gnews
    "title": "str",             # Parent document title
    "url": "str",               # Parent document URL
    "sentence_index": "int",    # Index of sentence in the original document
    "sentence_text": "str"      # The actual sentence text
}
