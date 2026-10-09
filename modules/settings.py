import streamlit as st
from database.database import query, execute
from modules.auth import logout
from pathlib import Path
import shutil
from datetime import datetime

def render_settings():
    uid=st.session_state.user_id
    st.title("⚙️ Settings")
    u=query("SELECT * FROM users WHERE id=?",(uid,))[0]
    st.subheader("Profile")
    with st.form("profile"):
        name=st.text_input("Name",u["name"])
        college=st.text_input("College",u["college"] or "")
        phone=st.text_input("Phone",u["phone"] or "")
        budget=st.number_input("Monthly budget ₹",min_value=0.0,value=float(u["monthly_budget"] or 0),step=100.0)
        goal=st.number_input("Monthly savings goal ₹",min_value=0.0,value=float(u["monthly_savings_goal"] or 0),step=100.0)
        if st.form_submit_button("Save profile"):
            execute("UPDATE users SET name=?,college=?,phone=?,monthly_budget=?,monthly_savings_goal=? WHERE id=?",(name,college,phone,budget,goal,uid))
            st.session_state.user_name=name; st.success("Profile updated.")
    st.subheader("Demo data")
    if st.button("Load Demo Data"):
        today=datetime.now().date()
        demo=[
            ("expense",80,"Food","College Canteen","UPI","Canteen"),
            ("expense",150,"Food","Food outside campus","UPI","Outside food"),
            ("expense",500,"Personal","Clothes","Debit Card","Clothes"),
            ("expense",120,"Travel","Auto","Cash","Auto"),
            ("expense",60,"Food","Tea/Coffee","Cash","Tea"),
            ("expense",300,"Education","Stationery","UPI","Stationery"),
            ("income",1500,"Money from Home",None,"Bank Transfer","Money received"),
            ("expense",2000,"Travel","Train","UPI","Travel"),
            ("expense",250,"Entertainment","Movies","UPI","Movie"),
            ("expense",100,"Education","Printing","Cash","Printing")
        ]
        for typ,amt,cat,sub,pay,desc in demo:
            execute("""INSERT INTO transactions(user_id,type,amount,category,subcategory,date,payment_method,description)
                       VALUES(?,?,?,?,?,?,?,?)""",(uid,typ,amt,cat,sub,str(today),pay,desc))
        st.success("Demo data loaded."); st.rerun()
    st.subheader("Backup")
    if st.button("Create SQLite backup"):
        p=Path("data/expenses.db")
        if p.exists():
            backup=Path("data")/f"expenses_backup_{datetime.now():%Y%m%d_%H%M%S}.db"
            shutil.copy2(p,backup)
            st.success(f"Backup created: {backup}")
        else: st.info("SQLite backup is available only when DATABASE_URL is not set.")
    st.subheader("Delete My Account")
    st.warning("This permanently deletes your account and associated financial data.")
    confirm=st.checkbox("I understand this cannot be undone.")
    if confirm and st.button("Delete My Account",type="primary"):
        # Explicit user-scoped deletion order.
        for table in ["trip_expenses","transactions","budgets","savings_goals","recurring_expenses","trips","categories","ai_insights"]:
            execute(f"DELETE FROM {table} WHERE user_id=?",(uid,))
        execute("DELETE FROM users WHERE id=?",(uid,))
        logout(); st.rerun()
