import os
from pathlib import Path

BASE_DIR = Path(os.environ.get("PDFCHAT_HOME", Path.home() / ".pdfchat"))
CHROMA_DIR = BASE_DIR / "chroma"

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
EMBED_MODEL = os.environ.get("PDFCHAT_EMBED_MODEL", "nomic-embed-text")
CHAT_MODEL = os.environ.get("PDFCHAT_CHAT_MODEL", "bonsai-2:4b")

CHUNK_MAX_CHARS = int(os.environ.get("PDFCHAT_CHUNK_MAX_CHARS", "1200"))
CHUNK_OVERLAP_SENTENCES = int(os.environ.get("PDFCHAT_CHUNK_OVERLAP", "1"))
TOP_K = int(os.environ.get("PDFCHAT_TOP_K", "6"))
