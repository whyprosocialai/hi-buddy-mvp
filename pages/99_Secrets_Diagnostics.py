import streamlit as st
from lib.firebase_utils import get_db

st.title("Secrets Diagnostics (safe)")
fb = st.secrets.get("firebase", {})
st.write("Firebase keys present:", sorted(list(fb.keys())))
st.write("Has service_account_json:", bool(fb.get("service_account_json", "").strip()))

# Try to init DB and show bound project + service account email (non-sensitive)
try:
    db = get_db()
    st.write("Firestore project:", getattr(db, "project", "<unknown>"))
    st.write("Service account email:", st.session_state.get("_debug_sa_email", "<unknown>"))
    st.success("Firestore client initialized.")
except Exception as e:
    st.error(f"Firestore init error: {e.__class__.__name__}: {e}")
