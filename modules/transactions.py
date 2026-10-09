import streamlit as st
import pandas as pd
from datetime import date
from database.database import query, insert_and_get_id, execute
from utils.helpers import EXPENSE_CATEGORIES, PAYMENTS, INCOME_CATEGORIES

def render_add_expense():
    uid=st.session_state.user_id
    st.title("➕ Add Expense")
    parents=list(EXPENSE_CATEGORIES)
    with st.form("expense"):
        amount=st.number_input("Amount ₹", min_value=0.01, step=10.0)
        parent=st.selectbox("Category", parents)
        subs=EXPENSE_CATEGORIES[parent]
        sub=st.selectbox("Sub-category", subs)
        d=st.date_input("Date", date.today())
        pay=st.selectbox("Payment method", PAYMENTS)
        desc=st.text_input("Description")
        loc=st.text_input("Location")
        notes=st.text_area("Optional notes")
        submit=st.form_submit_button("Save Expense", use_container_width=True)
    if submit:
        if amount <= 0: st.error("Amount must be positive."); return
        insert_and_get_id("""INSERT INTO transactions(user_id,type,amount,category,subcategory,date,payment_method,description,location,notes)
                          VALUES(?,?,?,?,?,?,?,?,?,?)""",
                         (uid,"expense",amount,parent,sub,str(d),pay,desc,loc,notes))
        st.success("Expense saved successfully. Dashboard updated.")
        st.rerun()

def render_add_income():
    uid=st.session_state.user_id
    st.title("💰 Add Money")
    with st.form("income"):
        amount=st.number_input("Amount ₹", min_value=0.01, step=100.0)
        source=st.selectbox("Source", INCOME_CATEGORIES)
        d=st.date_input("Date", date.today())
        pay=st.selectbox("Payment method", PAYMENTS)
        desc=st.text_input("Description")
        notes=st.text_area("Notes")
        submit=st.form_submit_button("Save Income", use_container_width=True)
    if submit:
        insert_and_get_id("""INSERT INTO transactions(user_id,type,amount,category,date,payment_method,description,notes)
                          VALUES(?,?,?,?,?,?,?,?)""",
                         (uid,"income",amount,source,str(d),pay,desc,notes))
        st.success("Income saved successfully.")
        st.rerun()

def render_transactions():
    uid=st.session_state.user_id
    st.title("💳 Transaction History")
    rows=query("SELECT * FROM transactions WHERE user_id=? ORDER BY date DESC,id DESC",(uid,))
    df=pd.DataFrame([dict(r) for r in rows]) if rows else pd.DataFrame()
    if df.empty:
        st.info("No transactions yet. Add income or an expense to get started."); return
    c1,c2,c3,c4=st.columns(4)
    search=c1.text_input("Search")
    typ=c2.selectbox("Type",["All","income","expense"])
    cats=["All"]+sorted(df["category"].dropna().unique().tolist())
    cat=c3.selectbox("Category",cats)
    pays=["All"]+sorted(df["payment_method"].dropna().unique().tolist())
    pay=c4.selectbox("Payment",pays)
    if search: df=df[df.astype(str).apply(lambda x:x.str.contains(search,case=False,na=False)).any(axis=1)]
    if typ!="All": df=df[df["type"]==typ]
    if cat!="All": df=df[df["category"]==cat]
    if pay!="All": df=df[df["payment_method"]==pay]
    st.dataframe(df[["id","date","type","category","subcategory","description","payment_method","amount","location"]], use_container_width=True, hide_index=True)
    st.download_button("⬇️ Export CSV", df.to_csv(index=False).encode(), "transactions.csv", "text/csv")
    st.subheader("Edit / Delete")
    tid=st.number_input("Transaction ID", min_value=1, step=1)
    if st.button("Delete selected transaction"):
        execute("DELETE FROM transactions WHERE id=? AND user_id=?",(int(tid),uid))
        st.success("Deleted."); st.rerun()
