"""Retrieval + grounded answering with validated [p. N] citations."""
import re

from .llm import chat
from .store import query
from .config import TOP_K

SYSTEM = (
    "You are a careful research assistant. Answer ONLY using the provided context. "
    "Every factual claim must cite its source page inline as [p. N]. "
    "If the context does not contain the answer, say exactly: I could not find that in the documents."
)

_CIT = re.compile(r"\[p\.\s*(\d+)\]")


def build_context(hits):
    return "\n\n".join(
        f"[{i}] p.{h['page']} ({h['source']}): {h['text']}" for i, h in enumerate(hits, 1)
    )


def validate_citations(answer: str, available_pages: set):
    """Strip citation tokens that reference pages that were never retrieved.

    Naive LLMs invent page numbers; we only trust pages present in context.
    Returns (clean_answer, valid_pages, invalid_pages).
    """
    valid, invalid = set(), set()
    for m in _CIT.finditer(answer):
        page = int(m.group(1))
        (valid if page in available_pages else invalid).add(page)

    def _sub(m):
        return m.group(0) if int(m.group(1)) in available_pages else ""

    clean = _CIT.sub(_sub, answer)
    return clean, valid, invalid


def answer_question(question: str, top_k: int = TOP_K):
    hits = query(question, top_k=top_k)
    if not hits:
        return {"answer": "No documents indexed yet. Ingest a PDF first.", "sources": [], "invalid_citations": []}
    context = build_context(hits)
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
    ]
    raw = chat(messages)
    pages = {h["page"] for h in hits}
    clean, valid, invalid = validate_citations(raw, pages)
    sources = sorted(
        [{"page": h["page"], "source": h["source"], "score": round(h["score"], 3)} for h in hits],
        key=lambda s: s["page"],
    )
    return {"answer": clean, "sources": sources, "valid_citations": sorted(valid), "invalid_citations": sorted(invalid)}
