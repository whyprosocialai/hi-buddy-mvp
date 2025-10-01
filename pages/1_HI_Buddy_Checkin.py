import datetime as dt
import streamlit as st
from lib.firebase_utils import require_auth, current_user, add_doc

st.set_page_config(page_title="HI-Buddy Check-in")
require_auth()

st.title("HI-Buddy · Daily Check-in")

mood = st.slider("Mood", 1, 5, 3)
energy = st.slider("Energy", 1, 5, 3)
stress = st.slider("Stress", 1, 5, 3)
flags = st.multiselect("Context", ["Slept well", "Heavy workload", "Socially intense", "Sick-ish"])
note = st.text_area("What's on your mind? (optional)", height=100)

if st.button("Save check-in"):
    u = current_user()
    add_doc(f"checkins/{u['uid']}/entries", {
        "ts": dt.datetime.utcnow().isoformat(),
        "mood": mood, "energy": energy, "stress": stress,
        "flags": flags, "note": note
    })
    st.success("Saved. See your progress on the Progress page.")
