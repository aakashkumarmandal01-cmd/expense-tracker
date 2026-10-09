import streamlit as st
import pandas as pd
from datetime import date
from database.database import query, insert_and_get_id, execute

def render_trips():
    uid=st.session_state.user_id
    st.title("✈️ Trips")
    with st.form("trip"):
        name=st.text_input("Trip name (e.g. Jaipur → Delhi)")
        start=st.date_input("Start",date.today())
        end=st.date_input("End",date.today())
        budget=st.number_input("Trip budget ₹",min_value=0.0,step=500.0)
        submit=st.form_submit_button("Create trip")
    if submit and name:
        insert_and_get_id("INSERT INTO trips(user_id,name,start_date,end_date,budget) VALUES(?,?,?,?,?)",(uid,name,str(start),str(end),budget))
        st.success("Trip created."); st.rerun()
    trips=query("SELECT * FROM trips WHERE user_id=? ORDER BY id DESC",(uid,))
    if not trips: st.info("Create a trip to track train, hotel, food, local transport and shopping."); return
    for t in trips:
        st.markdown(f"### {t['name']}")
        expenses=query("SELECT * FROM trip_expenses WHERE user_id=? AND trip_id=? ORDER BY date",(uid,t["id"]))
        total=sum(float(x["amount"]) for x in expenses)
        st.write(f"Total: ₹{total:,.0f} / Budget: ₹{t['budget']:,.0f}")
        if t["budget"]: st.progress(min(total/t["budget"],1))
        with st.expander("Add trip expense"):
            with st.form(f"trip_{t['id']}"):
                cat=st.selectbox("Category",["Train","Bus","Hotel","Food","Local transport","Shopping","Entertainment","Other"])
                amount=st.number_input("Amount ₹",min_value=0.01,step=50.0)
                d=st.date_input("Date",date.today(),key=f"d{t['id']}")
                desc=st.text_input("Description",key=f"x{t['id']}")
                ok=st.form_submit_button("Add")
            if ok:
                insert_and_get_id("INSERT INTO trip_expenses(user_id,trip_id,category,amount,date,description) VALUES(?,?,?,?,?,?)",(uid,t["id"],cat,amount,str(d),desc))
                st.rerun()
