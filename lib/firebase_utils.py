import os
import requests
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# ------------ Config helpers ------------
def _firebase_cfg():
    return st.secrets["firebase"]

def _api_key():
    return _firebase_cfg()["apiKey"]

@st.cache_resource
def _init_db():
    cfg = _firebase_cfg()
    service_account = cfg["service_account"]
    if not firebase_admin._apps:
        cred = credentials.Certificate(service_account)
        firebase_admin.initialize_app(cred)
    return firestore.client()

# Public accessors
def get_db():
    return _init_db()

# ------------ Auth via Firebase REST ------------
# Docs: https://identitytoolkit.googleapis.com/v1/

def _post(url, payload):
    r = requests.post(url, json=payload, timeout=20)
    r.raise_for_status()
    return r.json()

def sign_up(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={_api_key()}"
    data = _post(url, {"email": email, "password": password, "returnSecureToken": True})
    # optional: send verification email
    try:
        send_verification_email(data["idToken"])
    except Exception:
        pass
    return {"localId": data["localId"], "idToken": data["idToken"], "refreshToken": data.get("refreshToken")}

def sign_in(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={_api_key()}"
    data = _post(url, {"email": email, "password": password, "returnSecureToken": True})
    return {"localId": data["localId"], "idToken": data["idToken"], "refreshToken": data.get("refreshToken")}

def send_verification_email(id_token):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={_api_key()}"
    return _post(url, {"requestType": "VERIFY_EMAIL", "idToken": id_token})

# ------------ Session helpers ------------
def current_user():
    return st.session_state.get("user")

def require_auth():
    if "user" not in st.session_state:
        st.stop()

# ------------ Firestore helpers ------------
def upsert_doc(path, data: dict, merge=True):
    get_db().document(path).set(data, merge=merge)

def add_doc(path, data: dict):
    return get_db().collection(path).add(data)

def list_docs(path, limit=50, order_by=None, desc=True):
    db = get_db()
    col = db.collection(path)
    if order_by:
        from google.cloud import firestore as gcf
        col = col.order_by(order_by, direction=gcf.Query.DESCENDING if desc else gcf.Query.ASCENDING)
    return [{**d.to_dict(), "id": d.id} for d in col.limit(limit).stream()]
