import streamlit as st

def app_header():
    st.markdown("### HI-Buddy & eSokrates MVP")

def require_consent_gate():
    if not st.session_state.get("consented"):
        st.info("Please review and accept the Terms to continue.")
        if st.button("Go to Terms"):
            st.switch_page("streamlit_app.py")
        st.stop()

def sidebar_userbox():
    u = st.session_state.get("user")
    if u:
        st.sidebar.success(f"Signed in as {u.get('email','')}")
        if st.sidebar.button("Sign out"):
            for k in ["user", "consented", "profile"]:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()
