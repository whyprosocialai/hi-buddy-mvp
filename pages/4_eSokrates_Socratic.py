import datetime as dt
import streamlit as st
from lib.firebase_utils import require_auth, current_user, add_doc

st.set_page_config(page_title="eSokrates · Socratic")
require_auth()
st.title("Socratic Session")

q1 = st.text_input("1) What's the situation?")
q2 = st.text_input("2) What assumptions might you be making?")
q3 = st.text_input("3) What alternatives could exist?")
q4 = st.text_input("4) What's one tiny next step?")

if st.button("Save session"):
    u = current_user()
    add_doc(f"sessions/{u['uid']}/socratic", {
        "ts": dt.datetime.utcnow().isoformat(),
        "situation": q1, "assumptions": q2, "alternatives": q3, "next_step": q4
    })
    st.success("Saved.")
