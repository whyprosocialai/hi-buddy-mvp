import json, os, time
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pyrebase

# --- Read secrets (set these in Streamlit Secrets) ---
# st.secrets["firebase"] should contain:
# {
#   "apiKey": "...",
#   "authDomain": "...",
#   "projectId": "...",
#   "storageBucket": "...",
#   "messagingSenderId": "...",
#   "appId": "...",
#   "databaseURL": "https://<project>.firebaseio.com",
#   "service_account": { ... full service account json ... }
# }

@st.cache_resource
def _init_clients():
    cfg = dict(st.secrets["firebase"])
    service_account = cfg.pop("service_account")

    # Pyrebase for Auth
    pb = pyrebase.initialize_app(cfg)
    auth = pb.auth()

    # Admin SDK for Firestore
    if not firebase_admin._apps:
        cred = credentials.Certificate(service_account)
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    return auth, db

def clients():
    return _init_clients()

def sign_up(email, password):
    auth, _ = clients()
    user = auth.create_user_with_email_and_password(email, password)
    auth.send_email_verification(user['idToken'])
    return user

def sign_in(email, password):
    auth, _ = clients()
    user = auth.sign_in_with_email_and_password(email, password)
    return user

def refresh(id_token):
    auth, _ = clients()
    return auth.refresh(id_token)

def get_db():
    _, db = clients()
    return db

def current_user():
    """Return dict with uid/email from session, else None."""
    return st.session_state.get("user")

def require_auth():
    if "user" not in st.session_state:
        st.stop()

# --- Simple Firestore helpers ---
def upsert_doc(path, data: dict, merge=True):
    db = get_db()
    db.document(path).set(data, merge=merge)

def add_doc(path, data: dict):
    db = get_db()
    return db.collection(path).add(data)

def list_docs(path, limit=50, order_by=None, desc=True):
    db = get_db()
    col = db.collection(path)
    if order_by:
        col = col.order_by(order_by, direction=firestore.Query.DESCENDING if desc else firestore.Query.ASCENDING)
    return [ {**d.to_dict(), "id": d.id} for d in col.limit(limit).stream() ]
