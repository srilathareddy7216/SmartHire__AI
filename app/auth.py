"""
SmartHire — simple local authentication (login / signup).

Stores users in a local JSON file (data/users.json) with salted,
PBKDF2-hashed passwords. Uses only the Python standard library plus
Streamlit — no new dependency needed for requirements.txt.

NOTE: This is lightweight auth suitable for a demo / small internal
tool. It is NOT a replacement for a real user-management system —
there's no email verification, password reset, or rate limiting.
Treat data/users.json as sensitive local data (add it to .gitignore).
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
import secrets
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

# ---------------------------------------------------------------------------
# app/auth.py -> parent is app/, parent.parent is the project root
USERS_FILE = Path(__file__).resolve().parent.parent / "data" / "users.json"
PBKDF2_ITERATIONS = 260_000


# ---------------------------------------------------------------------------
# Storage helpers
# ---------------------------------------------------------------------------
def _ensure_store() -> None:
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not USERS_FILE.exists():
        USERS_FILE.write_text(json.dumps({}, indent=2))


def _load_users() -> dict:
    _ensure_store()
    try:
        return json.loads(USERS_FILE.read_text())
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def _save_users(users: dict) -> None:
    _ensure_store()
    USERS_FILE.write_text(json.dumps(users, indent=2))


# ---------------------------------------------------------------------------
# Password hashing (PBKDF2-HMAC-SHA256, per-user random salt)
# ---------------------------------------------------------------------------
def _hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    if salt is None:
        salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), PBKDF2_ITERATIONS
    ).hex()
    return digest, salt


def _verify_password(password: str, salt: str, expected_hash: str) -> bool:
    digest, _ = _hash_password(password, salt)
    return hmac.compare_digest(digest, expected_hash)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
_USERNAME_RE = re.compile(r"^[a-zA-Z0-9_.]{3,30}$")
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _validate_signup(username: str, email: str, password: str, confirm: str) -> str | None:
    if not _USERNAME_RE.match(username or ""):
        return "Username must be 3-30 characters (letters, numbers, '.', '_')."
    if not _EMAIL_RE.match(email or ""):
        return "Please enter a valid email address."
    if len(password or "") < 8:
        return "Password must be at least 8 characters."
    if password != confirm:
        return "Passwords do not match."
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def signup_user(username: str, email: str, password: str, confirm: str) -> tuple[bool, str]:
    username = (username or "").strip()
    email = (email or "").strip().lower()

    error = _validate_signup(username, email, password, confirm)
    if error:
        return False, error

    users = _load_users()
    if username.lower() in {u.lower() for u in users}:
        return False, "That username is already taken."
    if any(u.get("email") == email for u in users.values()):
        return False, "An account with that email already exists."

    digest, salt = _hash_password(password)
    users[username] = {
        "email": email,
        "password_hash": digest,
        "salt": salt,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _save_users(users)
    return True, "Account created! You can now log in from the Log In tab."


def login_user(username: str, password: str) -> tuple[bool, str]:
    username = (username or "").strip()
    users = _load_users()
    record = users.get(username)
    if not record or not _verify_password(password, record["salt"], record["password_hash"]):
        return False, "Incorrect username or password."
    return True, "Logged in."


def logout() -> None:
    for key in ("authenticated", "username"):
        st.session_state.pop(key, None)


def is_authenticated() -> bool:
    return bool(st.session_state.get("authenticated"))


# ---------------------------------------------------------------------------
# UI — colorful two-panel styling for the auth screen
# ---------------------------------------------------------------------------
_AUTH_CSS = """
<style>
/* Widen + center the whole auth layout instead of a narrow single column */
div[data-testid="stAppViewContainer"] .block-container:has(#sh-auth-anchor){
  max-width: 960px;
  padding-top: 3rem;
}

#sh-auth-anchor{ display:none; }

/* Hide Streamlit's built-in "Press Enter to submit/apply" hint under inputs */
div[data-testid="stAppViewContainer"] [data-testid="InputInstructions"]{
  display: none !important;
}

/* Left gradient hero panel — fills its column's full height */
.sh-auth-hero{
  height: 100%;
  min-height: 480px;
  padding: 2.4rem 2rem;
  border-radius: 22px;
  background: linear-gradient(160deg, #2F5BFF 0%, #7B5CFF 50%, #FF4FA3 100%);
  box-shadow: 0 14px 34px rgba(63, 60, 165, 0.28);
  color: #fff !important;
  display:flex; flex-direction:column; justify-content:center;
}
.sh-auth-hero .sh-auth-badge{
  width:64px; height:64px; margin-bottom: 1.2rem; border-radius:18px;
  background: rgba(255,255,255,0.18);
  display:flex; align-items:center; justify-content:center; font-size:1.9rem;
  border: 1px solid rgba(255,255,255,0.35);
}
.sh-auth-hero h1{
  color:#fff !important; font-family:'Space Grotesk', sans-serif !important;
  font-size:2.1rem; margin:0 0 0.6rem 0; letter-spacing:-0.02em; line-height:1.15;
}
.sh-auth-hero p{
  color: rgba(255,255,255,0.92) !important; font-size:0.98rem; margin:0 0 1.6rem 0;
  max-width: 320px;
}
.sh-auth-hero ul{ list-style:none; padding:0; margin:0; }
.sh-auth-hero li{
  color:#fff !important; font-size:0.9rem; margin-bottom:0.7rem;
  display:flex; align-items:center; gap:0.6rem;
}
.sh-auth-hero li .dot{
  width:8px; height:8px; border-radius:50%; background:#fff; flex:0 0 auto;
  box-shadow: 0 0 0 4px rgba(255,255,255,0.2);
}

/* Right panel container */
.sh-auth-panel{
  background:#fff; border:1px solid #E1E7F7; border-radius: 22px;
  padding: 1.8rem 2rem 1.4rem 2rem; height:100%;
  box-shadow: 0 4px 18px rgba(18,23,43,0.05);
}

/* Tabs — colorful pill style */
div[data-testid="stAppViewContainer"] .stTabs [data-baseweb="tab-list"]{
  gap: 8px; background: #EEF1FB; padding: 6px; border-radius: 14px;
  border: 1px solid #E1E7F7;
}
div[data-testid="stAppViewContainer"] .stTabs [data-baseweb="tab"]{
  flex:1; justify-content:center; border-radius: 10px !important;
  font-family:'Space Grotesk', sans-serif; font-weight:600; color:#6B7290;
  padding: 0.5rem 0.8rem;
}
div[data-testid="stAppViewContainer"] .stTabs [aria-selected="true"]{
  background: linear-gradient(90deg, #2F5BFF, #7B5CFF) !important;
  color: #fff !important;
  box-shadow: 0 6px 16px rgba(47,91,255,0.35);
}
div[data-testid="stAppViewContainer"] .stTabs [data-baseweb="tab-highlight"],
div[data-testid="stAppViewContainer"] .stTabs [data-baseweb="tab-border"]{
  display:none;
}

/* Form — no boxed card here, the panel above already provides one */
div[data-testid="stForm"]{
  border: none; padding: 1.1rem 0 0 0; background: transparent;
}

/* Inputs */
div[data-testid="stForm"] input{
  border-radius: 10px !important; border: 1.5px solid #E1E7F7 !important;
}
div[data-testid="stForm"] input:focus{
  border-color:#2F5BFF !important; box-shadow: 0 0 0 3px rgba(47,91,255,0.15) !important;
}

/* Buttons inside the login form = blue, inside signup = pink/purple */
#sh-login-marker + div [data-testid="stFormSubmitButton"] button{
  background: linear-gradient(90deg, #2F5BFF, #5B7FFF) !important;
  border:none !important; font-weight:700 !important; border-radius: 10px !important;
  box-shadow: 0 8px 20px rgba(47,91,255,0.3);
}
#sh-signup-marker + div [data-testid="stFormSubmitButton"] button{
  background: linear-gradient(90deg, #FF4FA3, #FF7A1A) !important;
  border:none !important; font-weight:700 !important; border-radius: 10px !important;
  box-shadow: 0 8px 20px rgba(255,79,163,0.3);
}
[data-testid="stFormSubmitButton"] button:hover{
  filter: brightness(1.06); transform: translateY(-1px);
}

.sh-auth-footnote{
  text-align:center; font-size:0.78rem; color:#6B7290; margin-top:1rem;
}

/* Hide Streamlit's default "Press Enter to submit form" / "Press Enter to apply" hint */
div[data-testid="stForm"] div[data-testid="InputInstructions"]{
  display: none !important;
}
</style>
"""


def render_auth_gate() -> None:
    """Renders a colorful two-panel Login / Sign up screen (gradient hero on
    the left, form on the right). Call this before any protected content,
    then st.stop() if is_authenticated() is still False."""
    st.markdown(_AUTH_CSS, unsafe_allow_html=True)
    st.markdown('<span id="sh-auth-anchor"></span>', unsafe_allow_html=True)

    left, right = st.columns([1, 1.15], gap="large")

    with left:
        st.markdown(
            '<div class="sh-auth-hero">'
            '<div class="sh-auth-badge">🔐</div>'
            '<h1>Welcome to<br>SmartHire</h1>'
            '<p>Match your resume to real jobs with classical ML — '
            'no LLMs, nothing sent to third parties.</p>'
            '<ul>'
            '<li><span class="dot"></span> Resume category prediction</li>'
            '<li><span class="dot"></span> Ranked job matches</li>'
            '<li><span class="dot"></span> Shortlisting fit score</li>'
            '<li><span class="dot"></span> Skill-gap report</li>'
            '</ul>'
            '</div>',
            unsafe_allow_html=True,
        )

    with right:
        st.markdown('<div class="sh-auth-panel">', unsafe_allow_html=True)
        tab_login, tab_signup = st.tabs(["🔵 Log In", "🌸 Sign Up"])

        with tab_login:
            st.markdown('<span id="sh-login-marker"></span>', unsafe_allow_html=True)
            with st.form("login_form", clear_on_submit=False):
                username = st.text_input("👤 Username")
                password = st.text_input("🔑 Password", type="password")
                submitted = st.form_submit_button("Log In →", type="primary", use_container_width=True)
            if submitted:
                ok, msg = login_user(username, password)
                if ok:
                    st.session_state.authenticated = True
                    st.session_state.username = username.strip()
                    st.rerun()
                else:
                    st.error(msg)

        with tab_signup:
            st.markdown('<span id="sh-signup-marker"></span>', unsafe_allow_html=True)
            with st.form("signup_form", clear_on_submit=False):
                new_username = st.text_input("👤 Choose a username")
                new_email = st.text_input("📧 Email")
                new_password = st.text_input("🔑 Password", type="password")
                confirm_password = st.text_input("🔑 Confirm password", type="password")
                submitted_signup = st.form_submit_button(
                    "Create Account ✨", type="primary", use_container_width=True
                )
            if submitted_signup:
                ok, msg = signup_user(new_username, new_email, new_password, confirm_password)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)

        st.markdown(
            '<p class="sh-auth-footnote">🔒 Passwords are salted &amp; hashed locally — never stored in plain text.</p>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)
