"""
File: app/rag/knowledge_loader.py
Purpose: Load startup methodology documents into ChromaDB on application startup.
Responsibilities:
  - Read knowledge text files from app/knowledge/
  - Chunk documents into manageable pieces
  - Generate embeddings and store in ChromaDB
  - Idempotent — skips loading if collection already has documents
Dependencies:
  - app.rag.embeddings (embed_texts)
  - app.rag.vector_store (get_knowledge_collection)
"""

import os
import uuid
from pathlib import Path

from app.rag.embeddings import embed_texts
from app.rag.vector_store import get_knowledge_collection

# Path to knowledge documents directory
KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"

# Target chunk size in characters
CHUNK_SIZE = 600
CHUNK_OVERLAP = 100


def chunk_text(text: str, source: str) -> list[dict]:
    """
    Purpose: Split a long document into overlapping chunks for better retrieval.
    Parameters:
      text: Full document text.
      source: Document name/source label.
    Returns:
      list[dict]: List of chunks with text and metadata.
    """
    chunks = []
    start = 0
    text = text.strip()

    while start < len(text):
        end = min(start + CHUNK_SIZE, len(text))

        # Try to break at a sentence boundary
        if end < len(text):
            period_pos = text.rfind(".", start, end)
            if period_pos > start + CHUNK_SIZE // 2:
                end = period_pos + 1

        chunk_text = text[start:end].strip()
        if chunk_text:
            chunks.append({
                "text": chunk_text,
                "source": source,
                "chunk_id": str(uuid.uuid4()),
            })

        start = end - CHUNK_OVERLAP

    return chunks


def load_knowledge_base() -> None:
    """
    Purpose: Load all knowledge documents into ChromaDB.
      Called once on application startup — idempotent.
    """
    collection = get_knowledge_collection()

    # Skip if already loaded
    if collection.count() > 0:
        print(f"✅ Knowledge base already loaded ({collection.count()} chunks)")
        return

    if not KNOWLEDGE_DIR.exists():
        print("⚠️  Knowledge directory not found, skipping RAG setup")
        return

    all_chunks = []

    for txt_file in KNOWLEDGE_DIR.glob("*.txt"):
        source_name = txt_file.stem.replace("_", " ").title()
        content = txt_file.read_text(encoding="utf-8")
        file_chunks = chunk_text(content, source_name)
        all_chunks.extend(file_chunks)
        print(f"  Loaded {len(file_chunks)} chunks from {txt_file.name}")

    if not all_chunks:
        print("⚠️  No knowledge files found")
        return

    # Generate embeddings in batch
    texts = [c["text"] for c in all_chunks]
    embeddings = embed_texts(texts)

    # Store in ChromaDB
    collection.add(
        ids=[c["chunk_id"] for c in all_chunks],
        documents=texts,
        embeddings=embeddings,
        metadatas=[{"source": c["source"]} for c in all_chunks],
    )

    print(f"✅ Knowledge base loaded: {len(all_chunks)} chunks from {len(list(KNOWLEDGE_DIR.glob('*.txt')))} files")
