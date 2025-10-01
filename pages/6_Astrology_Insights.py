import datetime as dt
import streamlit as st
from lib.firebase_utils import require_auth, current_user, get_db

st.set_page_config(page_title="Astrology Insights")
require_auth()
st.title("Astrology Insights (Optional)")

u = current_user()
doc = get_db().document(f"users/{u['uid']}").get()
ast = (doc.to_dict() or {}).get("astrology", {})

enabled = st.checkbox("Use astrology to shape daily reflections", value=ast.get("enabled", False))
bdate = st.date_input("Birth date", value=dt.date.fromisoformat(ast.get("birth_date")) if ast.get("birth_date") else dt.date(2000,1,1)) if enabled else None
btime = st.time_input("Birth time (optional)") if enabled else None
bcity = st.text_input("Birth city (optional)") if enabled else None

if st.button("Save settings"):
    get_db().document(f"users/{u['uid']}").set({
        "astrology": {
            "enabled": enabled,
            "birth_date": str(bdate) if bdate else None,
            "birth_time": str(btime) if btime else None,
            "birth_city": bcity
        }
    }, merge=True)
    st.success("Saved.")

st.markdown("#### Today’s Lens")
if enabled and bdate:
    # Super-simple, generic mapping to keep it non-infringing:
    day_num = (dt.date.today().toordinal() + bdate.toordinal()) % 3
    theme = ["Focus", "Connect", "Restore"][day_num]
    st.info(f"Suggested theme: **{theme}**")
    if theme == "Focus":
        st.write("Try a 25-minute focus block. Then run a quick Socratic question: ‘What matters most right now?’")
    elif theme == "Connect":
        st.write("Reach out to one supportive person. Journal for 2 minutes about what you need.")
    else:
        st.write("Take a short walk or 2-min breathing. Log a gentle check-in.")

    c1, c2 = st.columns(2)
    if c1.button("Open Daily Check-in"):
        st.switch_page("pages/1_HI_Buddy_Checkin.py")
    if c2.button("Start Socratic Session"):
        st.switch_page("pages/4_eSokrates_Socratic.py")
else:
    st.caption("Turn on astrology above to see a simple daily lens.")
