import streamlit as st
from lib.firebase_utils import sign_up, sign_in, upsert_doc, current_user, require_auth, get_db
from lib.ui import app_header, sidebar_userbox

st.set_page_config(page_title="HI-Buddy & eSokrates", page_icon="💫", layout="centered")
app_header()
sidebar_userbox()

# --- NAV STATES ---
if "stage" not in st.session_state:
    st.session_state.stage = "landing"  # landing | signin | signup | terms | onboarding | home

# --- ROUTER ---
stage = st.session_state.stage

def go(s):
    st.session_state.stage = s
    st.rerun()

# 0) LANDING
if stage == "landing":
    st.write("Welcome! Please sign in or create an account.")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Sign in"):
            go("signin")
    with c2:
        if st.button("Create account"):
            go("signup")
    st.markdown("---")
    st.caption("By continuing you agree to our basic Terms and Privacy summary shown after sign-up.")

# 0.2) SIGN IN
elif stage == "signin":
    with st.form("signin"):
        email = st.text_input("Email")
        pw = st.text_input("Password", type="password")
        submit = st.form_submit_button("Sign in")
    if submit:
        try:
            user = sign_in(email, pw)
            st.session_state.user = {"uid": user["localId"], "email": email, "idToken": user["idToken"], "refreshToken": user["refreshToken"]}
            # Load consent flag
            doc = get_db().document(f"users/{user['localId']}").get()
            st.session_state.consented = doc.to_dict().get("consented", False) if doc.exists else False
            go("home" if st.session_state.consented else "terms")
        except Exception as e:
            st.error(f"Sign in failed: {e}")

    if st.button("Back"):
        go("landing")

# 0.3) SIGN UP
elif stage == "signup":
    with st.form("signup"):
        email = st.text_input("Email")
        pw = st.text_input("Password", type="password")
        submit = st.form_submit_button("Create account")
    if submit:
        try:
            user = sign_up(email, pw)
            st.session_state.user = {"uid": user["localId"], "email": email, "idToken": user["idToken"], "refreshToken": user["refreshToken"]}
            go("terms")
        except Exception as e:
            st.error(f"Sign up failed: {e}")
    if st.button("Back"):
        go("landing")

# Terms & Consent
elif stage == "terms":
    st.subheader("Terms & Privacy (summary)")
    st.write(
        "- Your entries are stored securely in Google Firebase.\n"
        "- You can export or delete your data anytime in Settings.\n"
        "- This MVP is for testing only and not a medical device."
    )
    agree = st.checkbox("I agree to the Terms")
    consent = st.checkbox("I consent to storing my entries to personalize my experience")

    if st.button("Continue"):
        if not (agree and consent):
            st.warning("Please agree and consent to proceed.")
        else:
            u = current_user()
            upsert_doc(f"users/{u['uid']}", {"email": u["email"], "consented": True})
            st.session_state.consented = True
            go("onboarding")

# Onboarding (profile + goals + optional astrology)
elif stage == "onboarding":
    require_auth()
    st.subheader("Quick Profile")
    disp = st.text_input("Display name")
    tz = st.selectbox("Time zone", ["Auto", "US/Mountain", "US/Central", "US/Eastern", "Europe/Dublin"])
    remind = st.selectbox("Reminders", ["None", "Daily", "Weekly"])

    st.subheader("Goals (pick up to 3)")
    g1 = st.text_input("Goal 1", placeholder="e.g. Better sleep")
    g2 = st.text_input("Goal 2", placeholder="e.g. Less stress at work")
    g3 = st.text_input("Goal 3", placeholder="e.g. Move 20 min/day")

    st.subheader("Optional Astrology")
    use_ast = st.checkbox("Use astrology to shape daily reflections")
    bdate = st.date_input("Birth date") if use_ast else None
    btime = st.time_input("Birth time (optional)") if use_ast else None
    bcity = st.text_input("Birth city (optional)") if use_ast else None

    if st.button("Save & Continue"):
        u = current_user()
        upsert_doc(
            f"users/{u['uid']}",
            {
                "display_name": disp,
                "timezone": tz,
                "reminders": remind,
                "goals": [x for x in [g1, g2, g3] if x],
                "astrology": {"enabled": use_ast, "birth_date": str(bdate) if bdate else None,
                              "birth_time": str(btime) if btime else None, "birth_city": bcity}
            },
            merge=True
        )
        go("home")

# Home (jumping off point)
elif stage == "home":
    require_auth()
    st.success("You're in. Use the sidebar to open any page.")
    st.write("Quick actions:")
    c1, c2, c3 = st.columns(3)
    if c1.button("Daily check-in"):
        st.switch_page("pages/1_HI_Buddy_Checkin.py")
    if c2.button("Journal"):
        st.switch_page("pages/2_HI_Buddy_Journal.py")
    if c3.button("Socratic session"):
        st.switch_page("pages/4_eSokrates_Socratic.py")

    st.markdown("— Or use the left sidebar to navigate HI-Buddy, eSokrates, Astrology, Progress, and Settings.")
