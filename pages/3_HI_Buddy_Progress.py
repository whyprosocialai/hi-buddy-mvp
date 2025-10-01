import pandas as pd
import streamlit as st
from lib.firebase_utils import require_auth, current_user, list_docs

st.set_page_config(page_title="Progress")
require_auth()
st.title("Progress")

u = current_user()
rows = list_docs(f"checkins/{u['uid']}/entries", limit=90, order_by="ts")
if not rows:
    st.info("No check-ins yet. Try the Daily Check-in page.")
else:
    df = pd.DataFrame(rows)
    st.line_chart(df[["mood","energy","stress"]])
    st.write("Recent entries")
    st.dataframe(df[["ts","mood","energy","stress","flags"]].head(20))
