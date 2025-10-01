# lib/firebase_utils.py
import json
import requests
import streamlit as st
from google.cloud import firestore
from google.oauth2 import service_account

# ----------------- Config -----------------
def _cfg():
    return st.secrets["firebase"]

def _api_key():
    return _cfg()["apiKey"]

@st.cache_resource
def _db():
    cfg = _cfg()

    # Prefer a raw JSON string if provided
    sa_json = cfg.get("service_account_json", "").strip()
    sa = None

    if sa_json:
        try:
            sa = json.loads(sa_json)
        except Exception as e:
            raise ValueError(f"service_account_json is present but not valid JSON: {e}")

    if sa is None:
        raw = cfg.get("service_account", None)
        if raw is None:
            raise ValueError("No service account found. Add either [firebase].service_account_json (string) "
                             "or [firebase].service_account (table) in Streamlit Secrets.")
        # raw may be a TOML table/mapping or a JSON string
        sa = json.loads(raw) if isinstance(raw, str) else {k: raw[k] for k in raw.keys()}
        # normalize private key newlines if it came with literal \n
        pk = sa.get("private_key", "")
        if "\\n" in pk and "-----BEGIN PRIVATE KEY-----" in pk:
            sa["private_key"] = pk.replace("\\n", "\n")

    creds = service_account.Credentials.from_service_account_info(sa)
    db = firestore.Client(project=cfg["projectId"], credentials=creds)

    # lightweight (non-sensitive) debug
    st.session_state["_debug_db_project"] = db.project
    st.session_state["_debug_sa_email"] = sa.get("client_email", "")
    return db

def get_db():
    return _db()

# ----------------- Auth (REST) -----------------
# https://identitytoolkit.googleapis.com/v1/
def _post(url, payload):
    r = requests.post(url, json=payload, timeout=20)
    if r.status_code >= 400:
        try:
            detail = r.json().get("error", {}).get("message")
        except Exception:
            detail = r.text
        raise requests.HTTPError(f"{r.status_code} {r.reason}: {detail}")
    return r.json()

def sign_up(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={_api_key()}"
    data = _post(url, {"email": email, "password": password, "returnSecureToken": True})
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

# ----------------- Session helpers -----------------
def current_user():
    return st.session_state.get("user")

def require_auth():
    if "user" not in st.session_state:
        st.stop()

# ----------------- Firestore helpers -----------------
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
