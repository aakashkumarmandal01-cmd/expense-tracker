import streamlit as st
from datetime import date
from database.database import query, insert_and_get_id, execute
from utils.calculations import category_totals, month_bounds

def render_budgets():
    uid=st.session_state.user_id; today=date.today(); start,_=month_bounds(today.year,today.month)
    st.title("🎯 Budgets")
    with st.form("budget"):
        cat=st.text_input("Category (e.g. Food)")
        amount=st.number_input("Monthly budget ₹",min_value=0.0,step=100.0)
        submit=st.form_submit_button("Save Budget")
    if submit and cat.strip():
        execute("""INSERT INTO budgets(user_id,category,amount,month) VALUES(?,?,?,?)
                   ON CONFLICT(user_id,category,month) DO UPDATE SET amount=excluded.amount""",
                (uid,cat.strip(),amount,start.strftime("%Y-%m")))
        st.success("Budget saved."); st.rerun()
    budgets=query("SELECT * FROM budgets WHERE user_id=? AND month=?",(uid,start.strftime("%Y-%m")))
    actual={r["category"]:r["total"] for r in category_totals(uid,start,today)}
    if not budgets: st.info("No budgets set for this month."); return
    for b in budgets:
        spent=float(actual.get(b["category"],0)); limit=float(b["amount"]); pct=(spent/limit*100) if limit else 0
        st.write(f"**{b['category']}** — ₹{spent:,.0f} / ₹{limit:,.0f} ({pct:.0f}%)")
        st.progress(min(pct/100,1))
        if pct>=100: st.error(f"🔴 {b['category']} budget exceeded by ₹{spent-limit:,.0f}.")
        elif pct>=80: st.warning(f"⚠️ You have used {pct:.0f}% of your {b['category']} budget.")
