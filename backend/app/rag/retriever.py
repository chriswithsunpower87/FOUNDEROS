"""
File: app/rag/retriever.py
Purpose: Query the ChromaDB knowledge base to retrieve relevant context.
Responsibilities:
  - Embed the user's query using Sentence Transformers
  - Query ChromaDB for top-k similar knowledge chunks
  - Return concatenated context string for injection into agent prompts
Dependencies:
  - app.rag.embeddings (embed_text)
  - app.rag.vector_store (get_knowledge_collection)
"""

from app.rag.embeddings import embed_text
from app.rag.vector_store import get_knowledge_collection


def retrieve_context(query: str, n_results: int = 5, max_chars: int = 2000) -> str:
    """
    Purpose: Retrieve relevant startup methodology context for an idea.
    Parameters:
      query: The startup idea description to find relevant context for.
      n_results: Number of top-k chunks to retrieve (default 5).
      max_chars: Maximum total characters to return (prevents huge prompts).
    Returns:
      str: Concatenated relevant context passages ready to inject into prompts.
    """
    collection = get_knowledge_collection()

    # Check if collection has any documents
    if collection.count() == 0:
        return "No knowledge base context available."

    query_embedding = embed_text(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(n_results, collection.count()),
        include=["documents", "metadatas"],
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    if not documents:
        return "No relevant context found."

    # Assemble context string with source labels
    context_parts = []
    total_chars = 0

    for doc, meta in zip(documents, metadatas):
        source = meta.get("source", "Knowledge Base")
        chunk = f"[{source}]\n{doc}"

        if total_chars + len(chunk) > max_chars:
            break

        context_parts.append(chunk)
        total_chars += len(chunk)

    return "\n\n".join(context_parts)
