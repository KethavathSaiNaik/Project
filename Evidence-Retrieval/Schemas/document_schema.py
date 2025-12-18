# schemas/document_schema.py

"""
Document Schema

This schema defines the structure of a document returned by
the retrieval pipelines (Wikipedia, Scholar, GNews).

Each document belongs to exactly ONE user query.
"""

DOCUMENT_SCHEMA = {
    "query_id": "str",     # Unique identifier for the user query
    "doc_id": "str",       # Document ID (e.g., wiki_1, scholar_2, gnews_3)
    "source": "str",       # Source name: wikipedia | scholar | gnews
    "title": "str",        # Title of the document
    "url": "str",          # Source URL
    "text": "str"          # Raw document text (summary / abstract / description)
}
