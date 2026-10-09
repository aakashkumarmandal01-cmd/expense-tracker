from datetime import date
from calendar import monthrange
from database.database import query
from utils.calculations import totals, month_bounds

def forecast(uid):
    today=date.today(); start,_=month_bounds(today.year,today.month)
    _,spent,_=totals(uid,start,today)
    days=today.day
    avg=spent/days if days else 0
    days_in_month=monthrange(today.year,today.month)[1]
    expected=avg*days_in_month
    return {"spent":spent,"avg_daily":avg,"expected":expected,"remaining":max(expected-spent,0),"days":days_in_month}
