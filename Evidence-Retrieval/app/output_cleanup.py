import os
import shutil
import re
from collections import defaultdict

# All output subdirectories to manage
OUTPUT_DIRS = [
    "outputs/bm25",
    "outputs/documents",
    "outputs/explainability_faiss",
    "outputs/faiss",
    "outputs/fusion",
    "outputs/inference",
    "outputs/sentences",
]

MAX_QUERIES_TO_KEEP = 3

# Regex to extract query_id
QUERY_ID_PATTERN = re.compile(r"(q_\d{8}_\d{6}_[a-f0-9]+)")

def cleanup_old_queries():
    """
    Keeps only the latest MAX_QUERIES_TO_KEEP queries
    across all outputs/* directories.
    """

    # Collect query_ids globally
    query_ids = set()

    for base_dir in OUTPUT_DIRS:
        if not os.path.exists(base_dir):
            continue

        for name in os.listdir(base_dir):
            match = QUERY_ID_PATTERN.search(name)
            if match:
                query_ids.add(match.group(1))

    if len(query_ids) <= MAX_QUERIES_TO_KEEP:
        return

    # Sort query_ids chronologically (string sort works here)
    sorted_query_ids = sorted(query_ids)

    # Determine which to delete
    to_delete = sorted_query_ids[:-MAX_QUERIES_TO_KEEP]

    for base_dir in OUTPUT_DIRS:
        if not os.path.exists(base_dir):
            continue

        for name in os.listdir(base_dir):
            for qid in to_delete:
                if qid in name:
                    path = os.path.join(base_dir, name)

                    try:
                        if os.path.isdir(path):
                            shutil.rmtree(path)
                        else:
                            os.remove(path)
                    except Exception as e:
                        print(f"Cleanup failed for {path}: {e}")
