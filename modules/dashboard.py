import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, timedelta
from database.database import query
from utils.calculations import totals, category_totals, month_bounds
from utils.formatting import inr
from modules.ai_assistant import automatic_insights

def render_dashboard():
    uid=st.session_state.user_id
    today=date.today(); mstart,mend=month_bounds(today.year,today.month)
    income,expense,net=totals(uid)
    mi,me,mnet=totals(uid,mstart,today)
    days=today.day
    daily=me/days if days else 0
    month_budget=float(query("SELECT monthly_budget FROM users WHERE id=?",(uid,))[0]["monthly_budget"] or 0)
    remaining=month_budget-me if month_budget else 0
    tx_count=len(query("SELECT id FROM transactions WHERE user_id=?",(uid,)))
    week_start=today-timedelta(days=today.weekday())
    _,week_exp,_=totals(uid,week_start,today)
    _,today_exp,_=totals(uid,today,today)
    st.title(f"Your Financial Dashboard 👋")
    c=st.columns(4)
    c[0].metric("Total Money",inr(net))
    c[1].metric("Total Spent",inr(expense))
    c[2].metric("Total Received",inr(income))
    c[3].metric("Savings",inr(net))
    c=st.columns(6)
    c[0].metric("Today",inr(today_exp))
    c[1].metric("This Week",inr(week_exp))
    c[2].metric("This Month",inr(me))
    c[3].metric("Avg / Day",inr(daily))
    c[4].metric("Budget Left",inr(remaining) if month_budget else "—")
    c[5].metric("Transactions",tx_count)
    st.subheader("Spending overview")
    cats=category_totals(uid,mstart,today)
    if cats:
        df=pd.DataFrame([dict(x) for x in cats])
        fig=px.pie(df,names="category",values="total",hole=.5,title="This month's spending by category")
        st.plotly_chart(fig,use_container_width=True)
    else:
        st.info("No expenses this month yet. Add your first expense to see analytics.")
    st.subheader("AI insights")
    for insight in automatic_insights(uid)[:4]:
        st.info(insight)
