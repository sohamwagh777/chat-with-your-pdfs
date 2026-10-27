"""Ask a question over your indexed PDFs.

Usage:  python -m pdfchat.cli "your question" [--top-k 6]
"""
import argparse
import sys

from .rag import answer_question
from .config import TOP_K


def main(argv=None):
    ap = argparse.ArgumentParser(prog="pdfchat-ask", description="Ask a question over indexed PDFs")
    ap.add_argument("question")
    ap.add_argument("--top-k", type=int, default=TOP_K)
    args = ap.parse_args(argv)
    res = answer_question(args.question, top_k=args.top_k)
    print(res["answer"])
    if res["sources"]:
        print("\n--- sources ---")
        for s in res["sources"]:
            print(f"p.{s['page']}  {s['source']}  score={s['score']}")
    if res.get("invalid_citations"):
        print(f"\n(stripped {len(res['invalid_citations'])} hallucinated citation token(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
