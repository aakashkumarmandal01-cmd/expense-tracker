import streamlit as st
from database.database import init_db
from modules.auth import login_page, register_page, logout, render_password_reset_page
from modules.dashboard import render_dashboard
from modules.transactions import render_add_expense, render_add_income, render_transactions
from modules.analytics import render_analytics
from modules.budgets import render_budgets
from modules.savings import render_savings
from modules.trips import render_trips
from modules.recurring import render_recurring
from modules.ai_assistant import render_ai_assistant
from modules.settings import render_settings
from modules.onboarding import render_onboarding

st.set_page_config(page_title="College Expense Tracker", page_icon="🎓", layout="wide")

init_db()

# A reset link opens this public route before normal login/session checks.
reset_token = st.query_params.get("reset_token", "")
if reset_token:
    render_password_reset_page(reset_token)
    st.stop()

if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if st.session_state.user_id is None:
    tab1, tab2 = st.tabs(["Login", "Create Account"])
    with tab1:
        login_page()
    with tab2:
        register_page()
    st.stop()

if not st.session_state.get("onboarding_done", True):
    render_onboarding()
    st.stop()

st.markdown("""
<style>
.block-container {padding-top: 1.5rem; max-width: 1450px;}
[data-testid="stMetric"] {border: 1px solid rgba(128,128,128,.18); padding: 16px; border-radius: 14px;}
.card {padding:18px;border-radius:16px;border:1px solid rgba(128,128,128,.18);background:rgba(128,128,128,.04);}
.small-muted {color:#7a7a7a;font-size:.9rem;}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    user = st.session_state.get("user_name", "Student")
    st.markdown(f"## 🎓 College Finance")
    st.write(f"Welcome, **{user}** 👋")
    st.divider()
    pages = {
        "🏠 Dashboard":"Dashboard",
        "➕ Add Expense":"Add Expense",
        "💰 Add Money":"Add Money",
        "📊 Analytics":"Analytics",
        "💳 Transactions":"Transactions",
        "🎯 Budgets":"Budgets",
        "💎 Savings Goals":"Savings Goals",
        "✈️ Trips":"Trips",
        "🔄 Recurring Expenses":"Recurring Expenses",
        "🤖 AI Finance Assistant":"AI Finance Assistant",
        "⚙️ Settings":"Settings",
    }
    for label, value in pages.items():
        if st.button(label, use_container_width=True, type="primary" if st.session_state.page == value else "secondary"):
            st.session_state.page = value
            st.rerun()
    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        logout()
        st.rerun()

page = st.session_state.page
if page == "Dashboard":
    render_dashboard()
elif page == "Add Expense":
    render_add_expense()
elif page == "Add Money":
    render_add_income()
elif page == "Analytics":
    render_analytics()
elif page == "Transactions":
    render_transactions()
elif page == "Budgets":
    render_budgets()
elif page == "Savings Goals":
    render_savings()
elif page == "Trips":
    render_trips()
elif page == "Recurring Expenses":
    render_recurring()
elif page == "AI Finance Assistant":
    render_ai_assistant()
elif page == "Settings":
    render_settings()
