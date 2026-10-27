"""Sentence-aware Markdown chunker that never splits tables and carries page metadata."""
from dataclasses import dataclass
import re

from .config import CHUNK_MAX_CHARS, CHUNK_OVERLAP_SENTENCES

# split after sentence-ending punctuation followed by whitespace and a capital/digit/quote
_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9(\"\'])")


@dataclass
class Chunk:
    text: str
    page: int
    source: str


def is_table_line(line: str) -> bool:
    return line.lstrip().startswith("|")


def _units(text: str):
    """Split Markdown into atomic units.

    Prose is split on sentence boundaries; consecutive table rows form a
    single unit so a table is never fragmented across chunks.
    """
    units = []
    buf = []

    def flush_prose():
        nonlocal buf
        if buf:
            para = " ".join(buf).strip()
            buf = []
            if para:
                for s in _SENT_SPLIT.split(para):
                    s = s.strip()
                    if s:
                        units.append(("sentence", s))

    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if is_table_line(line):
            flush_prose()
            rows = []
            while i < len(lines) and is_table_line(lines[i]):
                rows.append(lines[i])
                i += 1
            units.append(("table", "\n".join(rows)))
        elif not line.strip():
            flush_prose()
            i += 1
        else:
            buf.append(line.strip())
            i += 1
    flush_prose()
    return units


def _render(units) -> str:
    parts = []
    for kind, val in units:
        parts.append(val)
    # sentences join with a space, tables keep their own lines
    out = []
    prev = None
    for (kind, val) in units:
        if prev is not None and kind == "sentence" and prev == "sentence":
            out.append(" ")
        elif prev is not None:
            out.append("\n")
        out.append(val)
        prev = kind
    return "".join(out)


def chunk_page(page_text: str, page_num: int, source: str,
               max_chars: int = CHUNK_MAX_CHARS,
               overlap: int = CHUNK_OVERLAP_SENTENCES):
    """Chunk one page of Markdown into size-bounded, sentence-aware chunks."""
    units = _units(page_text)
    if not units:
        return []

    chunks = []
    cur = []
    cur_len = 0
    for kind, val in units:
        add = len(val) + 1
        if cur and cur_len + add > max_chars:
            chunks.append(cur)
            # carry trailing sentence units forward as overlap
            tail = [(k, v) for (k, v) in cur if k == "sentence"][-overlap:] if overlap else []
            cur = list(tail)
            cur_len = sum(len(v) + 1 for _, v in cur)
        cur.append((kind, val))
        cur_len += add
    if cur:
        chunks.append(cur)

    return [Chunk(text=_render(c), page=page_num, source=source) for c in chunks]
