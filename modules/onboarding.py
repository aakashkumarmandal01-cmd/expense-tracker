import streamlit as st
from database.database import execute, query

def render_onboarding():
    uid = st.session_state.user_id
    st.title("Welcome to College Expense Tracker 🎓")
    st.write("Set your starting financial picture. You can change it later in Settings.")
    with st.form("onboarding"):
        budget = st.number_input("Monthly budget (₹)", min_value=0.0, step=100.0)
        savings = st.number_input("Monthly savings goal (₹)", min_value=0.0, step=100.0)
        current = st.number_input("Current available money (₹)", min_value=0.0, step=100.0)
        submit = st.form_submit_button("Create my dashboard", use_container_width=True)
    if submit:
        execute("UPDATE users SET monthly_budget=?, monthly_savings_goal=? WHERE id=?", (budget,savings,uid))
        if current > 0:
            execute("""INSERT INTO transactions(user_id,type,amount,date,payment_method,description)
                      VALUES(?,?,?,?,?,?)""",
                   (uid,"income",current,str(__import__("datetime").date.today()),"Bank Transfer","Starting balance"))
        st.session_state.onboarding_done = True
        st.rerun()
