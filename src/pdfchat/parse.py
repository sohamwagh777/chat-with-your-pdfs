"""PDF -> per-page Markdown using PyMuPDF4LLM."""
import pymupdf4llm


def pdf_to_pages(path: str):
    """Return a list of (page_number, markdown_text), 1-indexed."""
    results = pymupdf4llm.to_markdown(str(path), page_chunks=True, show_progress=False)
    pages = []
    for idx, entry in enumerate(results):
        text = entry.get("text", "") if isinstance(entry, dict) else str(entry)
        page_no = idx + 1
        if isinstance(entry, dict):
            page_no = entry.get("metadata", {}).get("page", idx + 1)
            try:
                page_no = int(page_no) + 1 if page_no == idx else int(page_no)
            except (TypeError, ValueError):
                page_no = idx + 1
        pages.append((page_no, text))
    return pages
