import streamlit as st
from lib.firebase_utils import require_auth, current_user, add_doc, list_docs, get_db

st.set_page_config(page_title="eSokrates · Actions")
require_auth()
st.title("Action Tracker")

u = current_user()
nexts = list_docs(f"sessions/{u['uid']}/socratic", limit=50, order_by="ts")
items = [ (r["id"], r.get("next_step","")) for r in nexts if r.get("next_step") ]

for i,(doc_id, label) in enumerate(items):
    col1, col2 = st.columns([3,1])
    col1.write(f"- {label}")
    if col2.button("Mark done", key=f"done_{i}"):
        db = get_db()
        db.collection(f"sessions/{u['uid']}/socratic").document(doc_id).set({"done": True}, merge=True)
        st.experimental_rerun()

if not items:
    st.info("No actions yet. Save a Socratic session with a next step.")
