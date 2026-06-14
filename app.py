import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from core.parser import extract_text, chunk_contract
from core.database import upsert_precedents, query_clause

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Precedent & Compliance Engine",
    page_icon="⚖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Minimal CSS polish
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    .section-label  { font-size:0.72rem; font-weight:700; text-transform:uppercase;
                      letter-spacing:0.08em; color:#6c757d; margin-bottom:4px; }
    .clause-box     { background:#f8f9fa; border:1px solid #dee2e6; border-radius:6px;
                      padding:14px; font-size:0.88rem; line-height:1.6; white-space:pre-wrap; }
    .similarity-tag { display:inline-block; background:#e9ecef; border-radius:12px;
                      padding:2px 10px; font-size:0.75rem; font-weight:600; margin-top:6px; }
    hr.divider      { border:none; border-top:1px solid #dee2e6; margin:20px 0; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar — upload historical contracts
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("Precedent Engine")
    st.caption("Upload historical contracts to expand the database.")
    st.markdown("---")

    uploaded_files = st.file_uploader(
        "Upload contracts (.txt, .pdf, .docx)",
        type=["txt", "pdf", "docx"],
        accept_multiple_files=True,
    )

    if uploaded_files:
        if st.button("Index Uploaded Contracts", use_container_width=True):
            with st.spinner("Parsing and indexing..."):
                for f in uploaded_files:
                    try:
                        text = extract_text(f, f.name)
                        chunks = chunk_contract(text)
                        contract_id = os.path.splitext(f.name)[0]
                        n = upsert_precedents(contract_id, chunks)
                        st.success(f"{f.name}: {n} chunks indexed")
                    except Exception as e:
                        st.error(f"{f.name}: {e}")

    st.markdown("---")
    st.caption("Contracts indexed here are stored in ChromaDB and used for precedent matching.")

# ---------------------------------------------------------------------------
# Main area
# ---------------------------------------------------------------------------
st.title("Precedent & Compliance Engine")
st.markdown(
    "Paste a customer redline clause below and click **Find Precedents** to retrieve the closest "
    "matching clauses from the historical contract database."
)

customer_clause = st.text_area(
    "Customer Redline Input",
    height=180,
    placeholder=(
        "Paste the clause the customer is proposing here...\n\n"
        'e.g. "The aggregate liability of either party shall not exceed USD $100,000 '
        "regardless of the nature of the claim, including data breaches, and this "
        'cap shall apply even in cases of gross negligence."'
    ),
)

search_btn = st.button("Find Precedents", type="primary", use_container_width=False)

if search_btn:
    if not customer_clause.strip():
        st.warning("Please paste a clause before searching.")
        st.stop()

    with st.spinner("Searching precedent database..."):
        precedents = query_clause(customer_clause, n_results=3)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="large")

    # Column 1 — Customer Redline
    with col1:
        st.markdown('<p class="section-label">Customer Redline</p>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="clause-box">{customer_clause.strip()}</div>',
            unsafe_allow_html=True,
        )

    # Column 2 — Precedent Matches
    with col2:
        st.markdown('<p class="section-label">Historical Precedents</p>', unsafe_allow_html=True)
        if not precedents:
            st.info("No precedents found in the database. Upload historical contracts via the sidebar.")
        else:
            for i, p in enumerate(precedents):
                sim_pct = int(p["similarity"] * 100)
                if sim_pct >= 75:
                    bar_color = "#28a745"
                elif sim_pct >= 45:
                    bar_color = "#ffc107"
                else:
                    bar_color = "#dc3545"

                st.markdown(
                    f'<div class="clause-box" style="margin-bottom:6px;">{p["text"]}</div>'
                    f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;">'
                    f'  <span class="similarity-tag">#{i+1} &nbsp;|&nbsp; {p["contract_id"]} &nbsp;|&nbsp; '
                    f'    <span style="color:{bar_color};font-weight:700;">{sim_pct}% match</span>'
                    f'  </span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown("---")
st.caption("Precedent & Compliance Engine — powered by ChromaDB + sentence-transformers")
