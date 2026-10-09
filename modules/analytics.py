import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, timedelta
from database.database import query
from utils.calculations import month_bounds, category_totals, totals

def render_analytics():
    uid=st.session_state.user_id
    st.title("📊 Expense Analytics")
    rows=query("SELECT * FROM transactions WHERE user_id=? AND type='expense' ORDER BY date",(uid,))
    if not rows: st.info("Add expenses to unlock analytics."); return
    df=pd.DataFrame([dict(r) for r in rows]); df["date"]=pd.to_datetime(df["date"])
    c1,c2=st.columns(2)
    with c1:
        fig=px.pie(df,names="category",values="amount",hole=.45,title="Spending by Category")
        st.plotly_chart(fig,use_container_width=True)
    with c2:
        p=df.groupby("payment_method",as_index=False)["amount"].sum()
        fig=px.bar(p,x="payment_method",y="amount",title="Digital vs Cash / Payment Method")
        st.plotly_chart(fig,use_container_width=True)
    daily=df.groupby("date",as_index=False)["amount"].sum()
    st.plotly_chart(px.line(daily,x="date",y="amount",markers=True,title="Daily Spending"),use_container_width=True)
    monthly=df.assign(month=df["date"].dt.to_period("M").astype(str)).groupby("month",as_index=False)["amount"].sum()
    st.plotly_chart(px.bar(monthly,x="month",y="amount",title="Monthly Spending"),use_container_width=True)
    st.subheader("Previous Month")
    today=date.today(); ps=month_bounds(today.year if today.month>1 else today.year-1, today.month-1 if today.month>1 else 12)
    _,prev,_=totals(uid,*ps); _,cur,_=totals(uid,month_bounds(today.year,today.month)[0],today)
    change=((cur-prev)/prev*100) if prev else 0
    st.metric("Previous month spending",f"₹{prev:,.0f}",delta=f"{change:+.1f}% vs previous month")
    if prev: st.write(f"You spent {'less' if cur<prev else 'more'} than the previous month.")
    st.subheader("Campus vs Outside Campus")
    outside=df[df["category"].isin(["Food","Travel","Entertainment","Personal"])]["amount"].sum()
    campus=df[~df["category"].isin(["Food","Travel","Entertainment","Personal"])]["amount"].sum()
    st.bar_chart(pd.DataFrame({"Campus":[campus],"Outside campus":[outside]}).T)
