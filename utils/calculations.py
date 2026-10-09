from datetime import date, timedelta
from database.database import query

def user_transactions(uid):
    return query("SELECT * FROM transactions WHERE user_id=? ORDER BY date DESC, id DESC", (uid,))

def totals(uid, start=None, end=None):
    clauses = ["user_id=?"]; params=[uid]
    if start: clauses.append("date>=?"); params.append(str(start))
    if end: clauses.append("date<=?"); params.append(str(end))
    rows = query(f"""SELECT type, COALESCE(SUM(amount),0) total
                     FROM transactions WHERE {' AND '.join(clauses)} GROUP BY type""", params)
    income = next((r["total"] for r in rows if r["type"]=="income"), 0)
    expense = next((r["total"] for r in rows if r["type"]=="expense"), 0)
    return float(income), float(expense), float(income-expense)

def balance(uid):
    return totals(uid)[2]

def month_bounds(year, month):
    start = date(year, month, 1)
    if month == 12: end = date(year+1,1,1)-timedelta(days=1)
    else: end = date(year,month+1,1)-timedelta(days=1)
    return start,end

def category_totals(uid, start=None, end=None):
    clauses=["user_id=?","type='expense'"]; params=[uid]
    if start: clauses.append("date>=?"); params.append(str(start))
    if end: clauses.append("date<=?"); params.append(str(end))
    return query(f"""SELECT COALESCE(category,'Other') category, SUM(amount) total
                     FROM transactions WHERE {' AND '.join(clauses)}
                     GROUP BY category ORDER BY total DESC""", params)
