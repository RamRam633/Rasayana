"""Streamlit UI — categorized browse + AI query. Calls the FastAPI core.

Run: streamlit run ui/app.py   (start `make api` first)
"""
from __future__ import annotations

import os

import httpx
import streamlit as st

BASE = os.environ.get("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Vayu Materia", page_icon="🌿", layout="wide")
st.title("🌿 Vayu Materia")
st.caption(
    "Knowledge hub for Indian traditional medicine — Ayurveda · Unani · Siddha · "
    "Sowa Rigpa · Yoga."
)
st.warning(
    "Traditional & research information, **not medical advice**. Every claim is shown "
    "with its evidence level and source. Consult a qualified practitioner.",
    icon="⚕️",
)


def api_get(path: str, **params):
    return httpx.get(f"{BASE}{path}", params=params, timeout=30.0).json()


browse, ask, srcs = st.tabs(["Browse plants", "Ask", "Sources"])

with browse:
    q = st.text_input("Search plants (scientific or vernacular name)", "")
    if q:
        rows = api_get("/plants", q=q, limit=25)
        if rows:
            st.dataframe(rows, use_container_width=True)
        else:
            st.info("No matches (the graph may be empty until you run an ingest).")

with ask:
    question = st.text_input("Ask a question", "Which plants contain withaferin A?")
    mode = st.radio("Mode", ["auto", "sql", "rag"], horizontal=True)
    if st.button("Ask") and question:
        payload = {"question": question, "mode": None if mode == "auto" else mode}
        try:
            r = httpx.post(f"{BASE}/query", json=payload, timeout=60.0)
            if r.status_code == 503:
                st.error(f"AI layer unavailable: {r.json().get('detail')}")
            else:
                data = r.json()
                st.write(data.get("answer"))
                if data.get("sql"):
                    st.code(data["sql"], language="sql")
                if data.get("rows"):
                    st.dataframe(data["rows"], use_container_width=True)
                if data.get("passages"):
                    for p in data["passages"]:
                        st.markdown(f"**{p.get('source','?')}** · score {p.get('score'):.2f}")
                        st.write(p.get("text"))
                if data.get("citations"):
                    st.caption("Sources: " + ", ".join(c["source_code"] for c in data["citations"]))
                st.caption(data.get("disclaimer", ""))
        except httpx.HTTPError as e:
            st.error(f"Request failed: {e}")

with srcs:
    st.subheader("Source registry")
    st.dataframe(api_get("/sources"), use_container_width=True)
