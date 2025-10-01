import datetime as dt
import streamlit as st
from lib.firebase_utils import require_auth, current_user, add_doc

st.set_page_config(page_title="HI-Buddy Journal")
require_auth()
st.title("Journal")

tags = st.multiselect("Tag", ["work", "relationships", "health", "other"])
text = st.text_area("Write freely", height=200)

col1, col2 = st.columns(2)
if col1.button("Save entry"):
    u = current_user()
    add_doc(f"journals/{u['uid']}/entries", {
        "ts": dt.datetime.utcnow().isoformat(),
        "text": text,
        "tags": tags
    })
    st.success("Saved.")
if col2.button("Reflect (scripted)"):
    st.info("• What matters most about this?\n• What would 'small but helpful' look like in 24 hours?\n• What support do you need?")
