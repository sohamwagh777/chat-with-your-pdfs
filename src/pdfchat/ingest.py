"""Ingest a PDF: pdf -> markdown -> chunks -> embeddings -> Chroma.

Usage:  python -m pdfchat.ingest <path.pdf> [--fresh]
"""
import argparse
import sys
from pathlib import Path

from .chunker import chunk_page
from .parse import pdf_to_pages
from .store import index_chunks, reset, count


def ingest_pdf(path: str, fresh: bool = False) -> dict:
    p = Path(path).expanduser().resolve()
    if not p.exists():
        raise FileNotFoundError(p)
    if fresh:
        reset()
    pages = pdf_to_pages(str(p))
    chunks = []
    for page_no, md in pages:
        chunks.extend(chunk_page(md, page_no, p.name))
    indexed = index_chunks(chunks)
    return {"file": p.name, "pages": len(pages), "chunks": len(chunks), "indexed": indexed, "total_in_store": count()}


def main(argv=None):
    ap = argparse.ArgumentParser(prog="pdfchat-ingest", description="Ingest a PDF into the local RAG store")
    ap.add_argument("pdf", help="path to a PDF file")
    ap.add_argument("--fresh", action="store_true", help="wipe the store before ingesting")
    args = ap.parse_args(argv)
    info = ingest_pdf(args.pdf, fresh=args.fresh)
    print(f"Indexed {info['indexed']} chunks from {info['file']} "
          f"({info['pages']} pages) | store now holds {info['total_in_store']} chunks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
