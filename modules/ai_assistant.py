import os, json
import streamlit as st
from datetime import date
from database.database import query
from utils.calculations import totals, category_totals, month_bounds
from utils.formatting import inr

def _data(uid):
    rows=query("""SELECT date,type,amount,category,subcategory,payment_method,description,location
                  FROM transactions WHERE user_id=? ORDER BY date DESC LIMIT 1000""",(uid,))
    user=query("SELECT name,college,monthly_budget,monthly_savings_goal FROM users WHERE id=?",(uid,))[0]
    return {"user":dict(user),"transactions":[dict(r) for r in rows]}

def automatic_insights(uid):
    today=date.today(); start,_=month_bounds(today.year,today.month)
    income,spent,net=totals(uid,start,today)
    cats=category_totals(uid,start,today)
    out=[]
    if spent and cats:
        top=dict(cats[0]); pct=float(top["total"])/spent*100
        out.append(f"💡 {top['category']} is {pct:.0f}% of your spending this month.")
    prev_start,prev_end=month_bounds(today.year if today.month>1 else today.year-1,today.month-1 if today.month>1 else 12)
    _,prev,_=totals(uid,prev_start,prev_end)
    if prev:
        change=(spent-prev)/prev*100
        out.append(f"{'⚠️' if change>10 else '📈'} Spending is {abs(change):.1f}% {'higher' if change>0 else 'lower'} than last month.")
    if income and net>0:
        out.append(f"🎯 You are currently saving {inr(net)} this month.")
    if not out: out=["💡 Add a few transactions to unlock personalized insights."]
    return out

def _fallback_answer(uid, prompt):
    p=prompt.lower(); today=date.today()
    if "today" in p:
        _,x,_=totals(uid,today,today); return f"You spent {inr(x)} today."
    if "this week" in p:
        from datetime import timedelta
        s=today-timedelta(days=today.weekday()); _,x,_=totals(uid,s,today); return f"You spent {inr(x)} this week."
    if "this month" in p:
        s,_=month_bounds(today.year,today.month); _,x,_=totals(uid,s,today); return f"You spent {inr(x)} this month."
    cats=category_totals(uid)
    if cats:
        return "Your highest spending categories are: " + ", ".join(f"{r['category']} ({inr(r['total'])})" for r in cats[:5]) + "."
    return "I need some transaction data before I can give a personalized answer."

def ask_ai(uid,prompt):
    key=os.getenv("OPENAI_API_KEY","").strip()
    if not key:
        return _fallback_answer(uid,prompt)
    try:
        from openai import OpenAI
        client=OpenAI(api_key=key)
        payload=_data(uid)
        system="""You are a college personal-finance assistant. Use ONLY the supplied user's financial data.
Never invent amounts. Be concise, practical, and transparent when data is insufficient.
Do not provide regulated investment/tax/legal advice. Treat affordability suggestions as budgeting guidance, not guarantees."""
        resp=client.responses.create(
            model=os.getenv("OPENAI_MODEL","gpt-5.6-mini"),
            instructions=system,
            input=f"User financial data JSON:\n{json.dumps(payload,default=str)}\n\nQuestion: {prompt}"
        )
        return resp.output_text
    except Exception as e:
        return _fallback_answer(uid,prompt) + f"\n\nAI API unavailable; local calculation used."

def render_ai_assistant():
    uid=st.session_state.user_id
    st.title("🤖 AI Finance Assistant")
    st.caption("AI sees only the currently logged-in user's financial records.")
    q=st.chat_input("Ask: How much did I spend on food this month?")
    if q:
        with st.chat_message("user"): st.write(q)
        answer=ask_ai(uid,q)
        with st.chat_message("assistant"): st.write(answer)
    st.subheader("Automatic insights")
    for x in automatic_insights(uid): st.info(x)
    if st.button("Generate Monthly Financial Report"):
        today=date.today(); start,_=month_bounds(today.year,today.month)
        inc,exp,save=totals(uid,start,today)
        cats=category_totals(uid,start,today)
        st.markdown(f"""### Monthly Summary
- Total income: {inr(inc)}
- Total expenses: {inr(exp)}
- Total savings: {inr(save)}

### Top Spending Categories
{chr(10).join(f"- {r['category']}: {inr(r['total'])}" for r in cats[:5])}
""")
