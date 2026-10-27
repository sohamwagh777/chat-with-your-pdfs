from pdfchat.chunker import chunk_page, _units

TABLE = (
    "# Results\n\n"
    "We evaluated three models.\n\n"
    "| Model | F1 | Pages |\n"
    "|---|---|---|\n"
    + "\n".join(f"| Model {i} | 0.{i}0 | {i} |" for i in range(1, 13))
    + "\n\nThe table above shows the headline numbers."
)


def test_table_never_split():
    chunks = chunk_page(TABLE, page_num=4, source="t.pdf", max_chars=120, overlap=0)
    table_chunks = [c for c in chunks if c.text.startswith("| Model | F1")]
    assert len(table_chunks) == 1, "whole table must live in exactly one chunk"
    body = table_chunks[0].text.splitlines()
    assert len([l for l in body if l.startswith("| Model ")]) == 13, "header + all 12 rows kept"


def test_chunks_carry_page_metadata():
    chunks = chunk_page("First sentence here. Second one follows.", page_num=7, source="a.pdf")
    assert chunks and all(c.page == 7 and c.source == "a.pdf" for c in chunks)


def test_sentence_boundary_ends():
    prose = " ".join(f"Sentence number {i} is here." for i in range(40))
    chunks = chunk_page(prose, page_num=1, source="a.pdf", max_chars=200, overlap=0)
    assert len(chunks) > 3
    for c in chunks:
        assert c.text.rstrip().endswith("."), "prose chunks must end on a sentence boundary"


def test_all_sentences_preserved():
    prose = " ".join(f"Sentence number {i} is here." for i in range(40))
    chunks = chunk_page(prose, page_num=1, source="a.pdf", max_chars=200, overlap=0)
    joined = " ".join(c.text for c in chunks)
    for i in range(40):
        assert f"Sentence number {i} is here." in joined


def test_overlap_adds_context():
    prose = " ".join(f"Sentence number {i} is here." for i in range(40))
    no_ov = chunk_page(prose, 1, "a.pdf", max_chars=200, overlap=0)
    ov = chunk_page(prose, 1, "a.pdf", max_chars=200, overlap=2)
    total_no = sum(len(c.text) for c in no_ov)
    total_ov = sum(len(c.text) for c in ov)
    assert total_ov > total_no, "overlap must duplicate a little context, never lose text"


def test_empty_page():
    assert chunk_page("   \n\n  ", 1, "a.pdf") == []
