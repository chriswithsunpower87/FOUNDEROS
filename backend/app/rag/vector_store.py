"""
File: app/rag/vector_store.py
Purpose: ChromaDB client setup and collection management.
Responsibilities:
  - Initialize ChromaDB with a persistent local storage path
  - Create or retrieve the startup knowledge collection
Dependencies:
  - chromadb
  - app.core.config (settings)
"""

from functools import lru_cache

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.core.config import settings

COLLECTION_NAME = "startup_knowledge"


@lru_cache(maxsize=1)
def get_chroma_client() -> chromadb.PersistentClient:
    """
    Purpose: Return a cached ChromaDB persistent client.
    Returns:
      chromadb.PersistentClient: Client connected to local persistent storage.
    Notes:
      - Data persists at settings.chroma_persist_path (./chroma_db by default)
      - @lru_cache ensures one client per process
    """
    return chromadb.PersistentClient(
        path=settings.chroma_persist_path,
        settings=ChromaSettings(anonymized_telemetry=False),
    )


def get_knowledge_collection() -> chromadb.Collection:
    """
    Purpose: Get or create the startup knowledge ChromaDB collection.
    Returns:
      chromadb.Collection: The knowledge base collection.
    """
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "Startup methodology and framework knowledge base"},
    )
