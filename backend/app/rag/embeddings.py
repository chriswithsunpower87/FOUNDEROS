"""
File: app/rag/embeddings.py
Purpose: Sentence Transformer embedding wrapper for the RAG pipeline.
Responsibilities:
  - Load the sentence-transformers model (runs locally, 100% free)
  - Convert text strings to vector embeddings for ChromaDB
Dependencies:
  - sentence-transformers
"""

from functools import lru_cache
from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """
    Purpose: Load and cache the sentence transformer model.
    Returns:
      SentenceTransformer: Loaded model (cached after first call).
    Notes:
      - Model: all-MiniLM-L6-v2 — fast, 384-dim embeddings, 80MB
      - Downloaded automatically on first use from HuggingFace
    """
    print("Loading sentence transformer model (first time only)...")
    return SentenceTransformer("all-MiniLM-L6-v2")


def embed_text(text: str) -> list[float]:
    """
    Purpose: Convert a single text string to a vector embedding.
    Parameters:
      text: The text to embed.
    Returns:
      list[float]: 384-dimensional embedding vector.
    """
    model = get_embedding_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Purpose: Convert multiple text strings to embeddings in one batch.
    Parameters:
      texts: List of texts to embed.
    Returns:
      list[list[float]]: List of 384-dimensional embedding vectors.
    """
    model = get_embedding_model()
    embeddings = model.encode(texts, convert_to_numpy=True, batch_size=32)
    return [e.tolist() for e in embeddings]
