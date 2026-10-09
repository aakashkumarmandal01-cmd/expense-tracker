import re
import bcrypt
import streamlit as st
from database.database import query, insert_and_get_id, execute

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD = 8

def _hash(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def _verify(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def register_page():
    st.subheader("Create your account")
    with st.form("register"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        college = st.text_input("College")
        phone = st.text_input("Phone (optional)")
        password = st.text_input("Password", type="password")
        confirm = st.text_input("Confirm password", type="password")
        submitted = st.form_submit_button("Create Account", use_container_width=True)
    if submitted:
        if not name.strip() or not college.strip():
            st.error("Name and college are required.")
        elif not EMAIL_RE.match(email.strip()):
            st.error("Enter a valid email address.")
        elif len(password) < MIN_PASSWORD:
            st.error("Password must be at least 8 characters.")
        elif password != confirm:
            st.error("Passwords do not match.")
        elif query("SELECT id FROM users WHERE lower(email)=lower(?)", (email.strip(),)):
            st.error("An account with this email already exists.")
        else:
            uid = insert_and_get_id(
                "INSERT INTO users(name,email,password_hash,college,phone) VALUES(?,?,?,?,?)",
                (name.strip(), email.strip().lower(), _hash(password), college.strip(), phone.strip())
            )
            st.session_state.user_id = uid
            st.session_state.user_name = name.strip()
            st.session_state.onboarding_done = False
            st.success("Account created. Continue with your personal setup.")
            st.rerun()

def login_page():
    st.subheader("Login")
    with st.form("login"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        remember = st.checkbox("Remember me")
        submitted = st.form_submit_button("Login", use_container_width=True)
    if submitted:
        rows = query("SELECT * FROM users WHERE lower(email)=lower(?)", (email.strip(),))
        if not rows or not _verify(password, rows[0]["password_hash"]):
            st.error("Invalid email or password.")
            return
        u = rows[0]
        st.session_state.user_id = u["id"]
        st.session_state.user_name = u["name"]
        st.session_state.user_email = u["email"]
        st.session_state.onboarding_done = True
        st.session_state.remember_me = remember
        st.success("Logged in.")
        st.rerun()
    with st.expander("Forgot password?"):
        st.info("For a production deployment, connect this flow to a verified email reset provider. This starter intentionally does not expose password-reset secrets in the app.")

def logout():
    for key in ["user_id","user_name","user_email","onboarding_done","remember_me"]:
        st.session_state.pop(key, None)
