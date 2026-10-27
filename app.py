"""Streamlit chat UI for pdfchat."""
import tempfile
from pathlib import Path

import streamlit as st

from pdfchat.ingest import ingest_pdf
from pdfchat.rag import answer_question
from pdfchat.store import count

st.set_page_config(page_title="Chat with your PDFs", page_icon="📄", layout="centered")
st.title("📄 Chat with your PDFs")
st.caption("100% local: Ollama embeddings + LLM, Chroma vector store. Your PDFs never leave your machine.")

with st.sidebar:
    st.header("Library")
    st.write(f"Chunks indexed: **{count()}**")
    up = st.file_uploader("Upload a PDF", type="pdf")
    if up is not None and st.button("Ingest PDF"):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(up.getbuffer())
            tmp_path = tmp.name
        with st.spinner("Parsing, chunking, embedding..."):
            info = ingest_pdf(tmp_path)
        st.success(f"Indexed {info['indexed']} chunks from {info['file']} ({info['pages']} pages)")

    sample = Path("sample_data/attention.pdf")
    if sample.exists() and st.button("Ingest sample: Attention Is All You Need"):
        info = ingest_pdf(str(sample))
        st.success(f"Indexed {info['indexed']} chunks (store total: {info['total_in_store']})")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if m.get("sources"):
            st.caption(" | ".join(f"p.{s['page']} {s['source']}" for s in m["sources"]))

if q := st.chat_input("Ask something about your PDFs..."):
    st.session_state.messages.append({"role": "user", "content": q})
    with st.chat_message("user"):
        st.markdown(q)
    with st.chat_message("assistant"):
        with st.spinner("Thinking locally..."):
            res = answer_question(q)
        st.markdown(res["answer"])
        if res["sources"]:
            st.caption(" | ".join(f"p.{s['page']} {s['source']}" for s in res["sources"]))
    st.session_state.messages.append(
        {"role": "assistant", "content": res["answer"], "sources": res["sources"]}
    )
