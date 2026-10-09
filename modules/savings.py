import streamlit as st
from database.database import query, insert_and_get_id, execute
from utils.formatting import inr
from utils.calculations import balance

def render_savings():
    uid=st.session_state.user_id
    st.title("💎 Savings Goals")
    with st.form("goal"):
        name=st.text_input("Goal name")
        target=st.number_input("Target amount ₹",min_value=1.0,step=500.0)
        current=st.number_input("Current saved ₹",min_value=0.0,step=100.0)
        submit=st.form_submit_button("Create Goal")
    if submit and name.strip():
        insert_and_get_id("INSERT INTO savings_goals(user_id,name,target_amount,current_amount) VALUES(?,?,?,?)",(uid,name,target,current))
        st.success("Goal created."); st.rerun()
    goals=query("SELECT * FROM savings_goals WHERE user_id=? ORDER BY id DESC",(uid,))
    if not goals: st.info("Create your first savings goal."); return
    for g in goals:
        pct=min(g["current_amount"]/g["target_amount"],1) if g["target_amount"] else 0
        st.markdown(f"### {g['name']}")
        st.write(f"{inr(g['current_amount'])} / {inr(g['target_amount'])} — {pct*100:.0f}%")
        st.progress(pct)
        st.caption(f"Remaining: {inr(max(g['target_amount']-g['current_amount'],0))}")
