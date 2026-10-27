from pdfchat.rag import validate_citations, build_context


def test_valid_citations_kept():
    ans = "Transformers use attention [p. 3]. The encoder stacks six layers [p. 5]."
    clean, valid, invalid = validate_citations(ans, {3, 5})
    assert clean == ans
    assert valid == {3, 5} and invalid == set()


def test_hallucinated_citation_stripped():
    ans = "Attention is all you need [p. 3]. It was tested on WMT 2014 [p. 99]."
    clean, valid, invalid = validate_citations(ans, {1, 2, 3})
    assert "[p. 99]" not in clean
    assert "[p. 3]" in clean
    assert valid == {3} and invalid == {99}


def test_no_citations_passes_through():
    ans = "No citations here at all."
    clean, valid, invalid = validate_citations(ans, {1})
    assert clean == ans and valid == set() and invalid == set()


def test_malformed_tokens_ignored():
    ans = "Odd [p.abc] and [p.] tokens stay, [p. 2] counts."
    clean, valid, invalid = validate_citations(ans, {2})
    assert valid == {2} and invalid == set()


def test_build_context_formats():
    hits = [{"text": "Some text", "page": 4, "source": "a.pdf", "score": 0.9}]
    ctx = build_context(hits)
    assert "[1] p.4 (a.pdf): Some text" in ctx
