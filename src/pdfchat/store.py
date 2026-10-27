"""Persistent Chroma vector store."""
import uuid

import chromadb

from .config import CHROMA_DIR
from .embeddings import embed

COLLECTION = "pdfchat"


def _client():
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(CHROMA_DIR))


def index_chunks(chunks):
    """Embed and store chunks. Returns number indexed."""
    if not chunks:
        return 0
    client = _client()
    col = client.get_or_create_collection(COLLECTION, metadata={"hnsw:space": "cosine"})
    vectors = embed([c.text for c in chunks])
    col.add(
        ids=[str(uuid.uuid4()) for _ in chunks],
        documents=[c.text for c in chunks],
        metadatas=[{"page": c.page, "source": c.source} for c in chunks],
        embeddings=vectors,
    )
    return len(chunks)


def query(text: str, top_k: int = 6):
    client = _client()
    col = client.get_or_create_collection(COLLECTION, metadata={"hnsw:space": "cosine"})
    if col.count() == 0:
        return []
    qv = embed([text])[0]
    res = col.query(query_embeddings=[qv], n_results=min(top_k, col.count()))
    hits = []
    for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        hits.append({"text": doc, "page": meta["page"], "source": meta["source"], "score": 1 - dist})
    return hits


def count():
    col = _client().get_or_create_collection(COLLECTION, metadata={"hnsw:space": "cosine"})
    return col.count()


def reset():
    client = _client()
    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass
