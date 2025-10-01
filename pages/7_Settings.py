import streamlit as st
from lib.firebase_utils import require_auth, current_user, get_db

st.set_page_config(page_title="Settings")
require_auth()
st.title("Settings")

u = current_user()
doc = get_db().document(f"users/{u['uid']}").get()
data = doc.to_dict() or {}

name = st.text_input("Display name", value=data.get("display_name",""))
tz = st.selectbox("Time zone", ["Auto","US/Mountain","US/Central","US/Eastern","Europe/Dublin"], index=0)
rem = st.selectbox("Reminders", ["None","Daily","Weekly"], index=0)

if st.button("Save"):
    get_db().document(f"users/{u['uid']}").set({
        "display_name": name, "timezone": tz, "reminders": rem
    }, merge=True)
    st.success("Saved.")

st.markdown("---")
if st.button("Export my data"):
    st.info("For MVP: copy/paste from Progress & Journal. Full export endpoint can be added later.")

if st.button("Delete my account"):
    st.warning("In MVP we’ll remove Firestore docs on request. (Auth deletion UI can be added later.)")
