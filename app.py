"""
app.py  ·  Document Intelligence Platform
Tabs: 💬 Chat | 📊 Analysis | 📥 Reports
Supports: PDF, Word (.docx), PowerPoint (.pptx), Excel (.xlsx), Image, TXT
"""

import os
import streamlit as st
from dotenv import load_dotenv

from rag.smart_loader import load_document, SUPPORTED_EXTENSIONS
from rag.chunker import chunk_pages
from rag.vector_store import add_chunks, get_indexed_sources, clear_collection
from rag.chain import answer_query, reset_client
from rag.memory import ConversationMemory
from rag.analyzer import analyze_document
from rag.report_exporter import export_to_pdf, export_to_docx, export_to_csv

load_dotenv()

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Document Intelligence Platform",
    page_icon="🧠",
    layout="wide",
)

# ── Session State ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "memory" not in st.session_state:
    st.session_state.memory = ConversationMemory(max_history=6)
if "indexed_files" not in st.session_state:
    st.session_state.indexed_files = {}          # filename -> pages list
if "analyses" not in st.session_state:
    st.session_state.analyses = {}               # filename -> analysis dict
# Auto-load API key from environment or .env
if "api_key_set" not in st.session_state:
    st.session_state.api_key_set = bool(os.getenv("GEMINI_API_KEY"))


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧠 Document Intelligence")
    st.caption("Chat · Analyze · Export Reports")
    st.divider()

    # ── API Key (auto-loaded, no entry needed) ──
    st.success("✅ Gemini API Ready (gemini-3.6-flash)")

    st.divider()

    # ── Upload ──
    st.subheader("📂 Upload Documents")
    file_types = SUPPORTED_EXTENSIONS
    uploaded_files = st.file_uploader(
        "PDF, Word, PPT, Excel, Image, TXT",
        type=file_types,
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded_files:
        if st.button("⚡ Index All Documents", use_container_width=True, type="primary"):
            new_files = [f for f in uploaded_files if f.name not in st.session_state.indexed_files]
            if not new_files:
                st.info("All files are already indexed.")
            else:
                progress = st.progress(0, text="Processing...")
                for i, ufile in enumerate(new_files):
                    with st.spinner(f"Processing {ufile.name}..."):
                        try:
                            raw = ufile.read()
                            pages = load_document(raw, ufile.name)
                            chunks = chunk_pages(pages)
                            add_chunks(chunks)
                            st.session_state.indexed_files[ufile.name] = pages
                            st.success(f"✅ {ufile.name} — {len(chunks)} chunks")
                        except Exception as e:
                            st.error(f"❌ {ufile.name}: {e}")
                    progress.progress((i + 1) / len(new_files))
                progress.empty()

    st.divider()

    # ── Indexed Docs ──
    st.subheader("📚 Indexed Documents")
    sources = get_indexed_sources()
    if sources:
        for src in sources:
            ext = src.rsplit(".", 1)[-1].upper() if "." in src else "?"
            icon = {"PDF": "📄", "DOCX": "📝", "PPTX": "📊", "XLSX": "📋",
                    "PNG": "🖼️", "JPG": "🖼️", "JPEG": "🖼️", "TXT": "📃"}.get(ext, "📄")
            st.markdown(f"{icon} `{src}`")
    else:
        st.caption("No documents indexed yet.")

    st.divider()

    # ── Settings ──
    st.subheader("⚙️ Settings")
    top_k = st.slider("Chunks to retrieve (Top-K)", 1, 10, 5)
    st.info("⚡ Model: **gemini-3.6-flash** (fixed)")
    model_name = None  # Always uses gemini-3.6-flash from gemini_client.py
    source_filter = st.selectbox(
        "Search in",
        ["All Documents"] + sources,
        help="Restrict Q&A to a specific document",
    )

    if st.button("🗑️ Clear All Data", use_container_width=True):
        clear_collection()
        st.session_state.update({
            "indexed_files": {},
            "analyses": {},
            "messages": [],
            "memory": ConversationMemory(max_history=6),
        })
        st.rerun()

# ── Main Area — 3 Tabs ────────────────────────────────────────────────────────
tab_chat, tab_analysis, tab_reports = st.tabs(["💬 Chat", "📊 Analysis", "📥 Reports"])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — CHAT
# ═══════════════════════════════════════════════════════════════════════════════
with tab_chat:
    st.markdown("### 💬 Ask Questions About Your Documents")
    st.caption("Multi-turn chat with memory — ask follow-ups naturally!")

    # Display history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander("📎 Sources", expanded=False):
                    for src in msg["sources"]:
                        st.markdown(
                            f"**{src['source']}** — Page {src['page']} "
                            f"*(relevance: {src['score']:.0%})*"
                        )
                        st.caption(src["text"][:300] + "..." if len(src["text"]) > 300 else src["text"])
                        st.divider()

    # Input
    if prompt := st.chat_input("Ask anything about your documents..."):
        if not st.session_state.api_key_set and not os.getenv("GEMINI_API_KEY"):
            st.error("⚠️ Please enter your Gemini API key in the sidebar first.")
            st.stop()

        st.session_state.memory.add_user(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("🔍 Searching & generating answer..."):
                try:
                    answer, sources = answer_query(
                        query=prompt,
                        top_k=top_k,
                        model_name=model_name,
                        history_text=st.session_state.memory.get_history_text(),
                        source_filter=source_filter,
                    )
                except Exception as e:
                    answer = f"❌ Error: {e}"
                    sources = []

            st.markdown(answer)
            if sources:
                with st.expander("📎 Sources", expanded=False):
                    for src in sources:
                        st.markdown(
                            f"**{src['source']}** — Page {src['page']} "
                            f"*(relevance: {src['score']:.0%})*"
                        )
                        st.caption(src["text"][:300] + "..." if len(src["text"]) > 300 else src["text"])
                        st.divider()

        st.session_state.memory.add_assistant(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer, "sources": sources})

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🧹 Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.memory.clear()
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_analysis:
    st.markdown("### 📊 Automatic Document Analysis")
    st.caption("Generate a full structured report: Summary · Key Points · Entities · Sentiment · Suggested Questions")

    if not st.session_state.indexed_files:
        st.info("📂 Upload and index a document first using the sidebar.")
    else:
        # Select document to analyze
        doc_names = list(st.session_state.indexed_files.keys())
        selected_doc = st.selectbox("Select document to analyze", doc_names)

        col_btn, col_status = st.columns([2, 3])
        with col_btn:
            analyze_btn = st.button(
                "🔬 Generate Analysis Report",
                use_container_width=True,
                type="primary",
                disabled=not bool(os.getenv("GEMINI_API_KEY")),
            )

        if analyze_btn:
            with st.spinner(f"Analyzing {selected_doc} with Gemini (auto)..."):
                try:
                    pages = st.session_state.indexed_files[selected_doc]
                    analysis = analyze_document(pages, selected_doc, model_name=model_name)
                    st.session_state.analyses[selected_doc] = analysis
                    st.success("✅ Analysis complete!")
                except Exception as e:
                    st.error(f"❌ Analysis failed: {e}")

        # Show analysis if available
        if selected_doc in st.session_state.analyses:
            analysis = st.session_state.analyses[selected_doc]
            st.divider()
            st.markdown(f"#### 📄 Report for: `{analysis['filename']}`")
            st.caption(f"Pages/Sections: {analysis['page_count']}  |  Characters: {analysis['char_count']:,}")
            st.markdown(analysis["raw_report"])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — REPORTS / EXPORT
# ═══════════════════════════════════════════════════════════════════════════════
with tab_reports:
    st.markdown("### 📥 Download Analysis Reports")
    st.caption("Export your analysis as PDF, Word document, or CSV spreadsheet.")

    if not st.session_state.analyses:
        st.info("📊 Go to the **Analysis** tab first and generate a report for a document.")
    else:
        report_doc = st.selectbox(
            "Select analysed document",
            list(st.session_state.analyses.keys()),
            key="report_select",
        )
        analysis = st.session_state.analyses[report_doc]

        st.markdown(f"**Document:** `{analysis['filename']}`  |  **Sections:** {analysis['page_count']}  |  **Chars:** {analysis['char_count']:,}")
        st.divider()

        col_pdf, col_word, col_csv = st.columns(3)

        with col_pdf:
            st.markdown("#### 📄 PDF Report")
            st.caption("Styled, print-ready PDF")
            try:
                pdf_bytes = export_to_pdf(analysis)
                st.download_button(
                    label="⬇️ Download PDF",
                    data=pdf_bytes,
                    file_name=f"{report_doc}_analysis.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"PDF error: {e}")

        with col_word:
            st.markdown("#### 📝 Word Document")
            st.caption("Editable .docx file")
            try:
                docx_bytes = export_to_docx(analysis)
                st.download_button(
                    label="⬇️ Download Word",
                    data=docx_bytes,
                    file_name=f"{report_doc}_analysis.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"Word error: {e}")

        with col_csv:
            st.markdown("#### 📊 CSV Spreadsheet")
            st.caption("Open in Excel / Google Sheets")
            try:
                csv_bytes = export_to_csv(analysis)
                st.download_button(
                    label="⬇️ Download CSV",
                    data=csv_bytes,
                    file_name=f"{report_doc}_analysis.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"CSV error: {e}")

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("🧠 Document Intelligence Platform · Gemini 2.5 · ChromaDB · sentence-transformers · Streamlit")
