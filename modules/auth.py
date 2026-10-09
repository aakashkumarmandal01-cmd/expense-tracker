import re
import bcrypt
import streamlit as st
from database.database import query, insert_and_get_id, execute
import hashlib
import secrets
import smtplib
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage

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

def render_password_reset_page():
    """Request a reset email or set a new password using a reset token."""

    # Create the token table if it does not exist.
    execute("""
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            token_hash TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            used INTEGER NOT NULL DEFAULT 0
        )
    """)

    st.subheader("Reset your password")

    # Read the token from the URL.
    token = st.query_params.get("reset_token", "")

    if token:
        with st.form("set_new_password"):
            password = st.text_input("New password", type="password")
            confirm = st.text_input("Confirm new password", type="password")
            submitted = st.form_submit_button("Update password")

        if submitted:
            if len(password) < MIN_PASSWORD:
                st.error("Password must be at least 8 characters.")
                return

            if password != confirm:
                st.error("Passwords do not match.")
                return

            token_hash = hashlib.sha256(token.encode()).hexdigest()
            rows = query(
                """SELECT id, user_id, expires_at FROM password_reset_tokens
                   WHERE token_hash = ? AND used = 0""",
                (token_hash,)
            )

            if not rows:
                st.error("Invalid or already-used reset link.")
                return

            row = rows[0]
            try:
                expiry = datetime.fromisoformat(row["expires_at"])
                if expiry.tzinfo is None:
                    expiry = expiry.replace(tzinfo=timezone.utc)
            except (ValueError, TypeError, KeyError):
                st.error("Invalid reset link. Please request a new one.")
                return

            if datetime.now(timezone.utc) >= expiry:
                st.error("This reset link has expired. Request a new one.")
                return

            execute(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (_hash(password), row["user_id"])
            )
            execute(
                "UPDATE password_reset_tokens SET used = 1 WHERE id = ?",
                (row["id"],)
            )

            st.success("Password updated. You can now log in.")
            st.query_params.clear()
        return

    st.write("Enter the email address associated with your account.")
    with st.form("request_password_reset"):
        email = st.text_input("Registered email")
        submitted = st.form_submit_button("Send reset link")

    if submitted:
        email = email.strip().lower()

        if not EMAIL_RE.match(email):
            st.error("Enter a valid email address.")
            return

        users = query(
            "SELECT id FROM users WHERE lower(email) = lower(?)",
            (email,)
        )

        # Avoid revealing whether an email is registered.
        if not users:
            st.success(
                "If an account exists for that email, a reset link will be sent."
            )
            return

        try:
            settings = st.secrets
            smtp_user = settings["SMTP_USER"]
            smtp_password = settings["SMTP_PASSWORD"]
            app_url = settings["APP_URL"].rstrip("?&")

            raw_token = secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
            expiry = (
                datetime.now(timezone.utc) + timedelta(minutes=30)
            ).isoformat()

            execute(
                """INSERT INTO password_reset_tokens
                   (user_id, token_hash, expires_at, used)
                   VALUES (?, ?, ?, 0)""",
                (users[0]["id"], token_hash, expiry)
            )

            separator = "&" if "?" in app_url else "?"
            reset_url = f"{app_url}{separator}reset_token={raw_token}"

            message = EmailMessage()
            message["Subject"] = "Password reset - College Expense Tracker"
            message["From"] = settings.get("SMTP_FROM", smtp_user)
            message["To"] = email
            message.set_content(
                "You requested a password reset.\n\n"
                f"Open this link to reset your password:\n{reset_url}\n\n"
                "This link expires in 30 minutes. "
                "If you did not request it, ignore this email."
            )

            with smtplib.SMTP(
                settings.get("SMTP_HOST", "smtp.gmail.com"),
                int(settings.get("SMTP_PORT", 587)),
                timeout=20
            ) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(message)

            st.success("If an account exists for that email, a reset link will be sent.")

        except Exception:
            st.error(
                "Could not send the reset email. Check your Streamlit Secrets "
                "and database configuration, then try again."
            )
