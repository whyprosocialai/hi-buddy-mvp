import streamlit as st
from lib.firebase_utils import require_auth

st.set_page_config(page_title="Help")
require_auth()
st.title("Help & About")

st.write("""
- This is an MVP for HI-Buddy (daily check-ins, nudges, journaling) and eSokrates (Socratic micro-dialogue).
- Your entries are stored securely in Firebase. You can opt out any time in Settings.
- If AI is unavailable, you will still get scripted prompts so the app remains useful.
""")
