import os
import json
import shutil
from typing import Optional

from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_groq import ChatGroq

# -----------------------------------------------------
# Environment
# -----------------------------------------------------
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not found in environment")

# -----------------------------------------------------
# Global state (one query at a time)
# -----------------------------------------------------
ACTIVE_QUERY_ID: Optional[str] = None
FAISS_BASE_DIR = "outputs/explainability_faiss"

# -----------------------------------------------------
# System prompt (ASCII only)
# -----------------------------------------------------
SYSTEM_PROMPT = """
You are an evidence grounded explainability assistant.

A fact verification system has already produced a final decision.

Rules:
- Do not change or override the decision.
- Do not introduce external knowledge.
- Do not hallucinate information.
- Use only the retrieved evidence.
- If evidence is insufficient, clearly say so.

Your role is explanation only.
"""

# -----------------------------------------------------
# Build FAISS index AFTER NLI
# -----------------------------------------------------
def build_explainability_index(query_id: str, top_k: int = 5):
    global ACTIVE_QUERY_ID

    # Delete old FAISS index if exists
    if ACTIVE_QUERY_ID:
        old_path = os.path.join(FAISS_BASE_DIR, ACTIVE_QUERY_ID)
        if os.path.exists(old_path):
            shutil.rmtree(old_path)

    ACTIVE_QUERY_ID = query_id

    os.makedirs(FAISS_BASE_DIR, exist_ok=True)

    fusion_path = f"outputs/fusion/final_ranked_sentences_{query_id}.json"
    docs_path = f"outputs/documents/documents_{query_id}.json"

    with open(fusion_path, "r", encoding="utf-8") as f:
        fusion_data = json.load(f)

    with open(docs_path, "r", encoding="utf-8") as f:
        docs_data = json.load(f)

    top_doc_ids = []
    for s in fusion_data["results"][:top_k]:
        doc_id = s.get("doc_id")
        if doc_id and doc_id not in top_doc_ids:
            top_doc_ids.append(doc_id)

    texts = []
    metadatas = []

    for doc in docs_data["documents"]:
        if doc["doc_id"] in top_doc_ids:
            texts.append(doc["text"])
            metadatas.append({
                "doc_id": doc["doc_id"],
                "source": doc.get("source"),
                "title": doc.get("title"),
                "url": doc.get("url")
            })

    if not texts:
        return

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    faiss_index = FAISS.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metadatas
    )

    save_path = os.path.join(FAISS_BASE_DIR, query_id)
    faiss_index.save_local(save_path)

# -----------------------------------------------------
# Chatbot query (loads FAISS from disk)
# -----------------------------------------------------
def answer_user_question(
    query_id: str,
    user_question: str,
    final_label: str,
    confidence: float
):
    if query_id != ACTIVE_QUERY_ID:
        return "Explainability index not available for this query."

    faiss_path = os.path.join(FAISS_BASE_DIR, query_id)
    if not os.path.exists(faiss_path):
        return "Explainability index not found."

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = FAISS.load_local(
        faiss_path,
        embeddings,
        allow_dangerous_deserialization=True
    )

    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    relevant_docs = retriever.invoke(user_question)

    if not relevant_docs:
        return "The available evidence does not answer this question."

    context = ""
    for i, doc in enumerate(relevant_docs, start=1):
        context += (
            f"{i}. {doc.page_content}\n"
            f"(Source: {doc.metadata.get('source')}, "
            f"Title: {doc.metadata.get('title')})\n\n"
        )

    llm = ChatGroq(
        groq_api_key=GROQ_API_KEY,
        model_name="llama-3.1-8b-instant",
        temperature=0.2,
        max_tokens=1024,
    )

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"""
Final decision: {final_label}
Confidence: {confidence}

Evidence:
{context}

User question:
{user_question}

Answer using only the evidence above.
""")
    ])

    response = llm.invoke(prompt.format())
    return response.content
