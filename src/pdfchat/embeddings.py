"""Local embeddings via Ollama (nomic-embed-text). Nothing leaves your machine."""
import requests

from .config import OLLAMA_URL, EMBED_MODEL


def embed(texts, batch_size: int = 32):
    if not texts:
        return []
    vectors = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        r = requests.post(
            f"{OLLAMA_URL}/api/embed",
            json={"model": EMBED_MODEL, "input": batch},
            timeout=120,
        )
        if r.status_code == 404:  # older Ollama without /api/embed
            r = requests.post(
                f"{OLLAMA_URL}/api/embeddings",
                json={"model": EMBED_MODEL, "prompt": batch[0]},
                timeout=120,
            )
            r.raise_for_status()
            vectors.append(r.json()["embedding"])
            continue
        r.raise_for_status()
        vectors.extend(r.json()["embeddings"])
    return vectors
