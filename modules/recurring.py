import streamlit as st
from datetime import date
from database.database import query, insert_and_get_id
from utils.helpers import PAYMENTS

def render_recurring():
    uid=st.session_state.user_id
    st.title("🔄 Recurring Expenses")
    with st.form("recurring"):
        name=st.text_input("Name")
        amount=st.number_input("Amount ₹",min_value=0.01,step=50.0)
        freq=st.selectbox("Frequency",["Weekly","Monthly","Quarterly","Yearly"])
        next_date=st.date_input("Next payment date",date.today())
        category=st.text_input("Category")
        submit=st.form_submit_button("Add recurring expense")
    if submit:
        insert_and_get_id("""INSERT INTO recurring_expenses(user_id,name,amount,frequency,next_payment_date,category)
                          VALUES(?,?,?,?,?,?)""",(uid,name,amount,freq,str(next_date),category))
        st.success("Recurring expense added."); st.rerun()
    rows=query("SELECT * FROM recurring_expenses WHERE user_id=? AND active=1 ORDER BY next_payment_date",(uid,))
    if rows:
        st.dataframe([dict(r) for r in rows],use_container_width=True,hide_index=True)
    else: st.info("No recurring expenses.")
