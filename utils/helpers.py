import calendar
from datetime import date
import pandas as pd

EXPENSE_CATEGORIES = {
"Food":["College Canteen","Mess","Food outside campus","Restaurant","Café","Snacks","Fast food","Swiggy/Zomato","Groceries","Tea/Coffee","Water/Drinks"],
"Education":["Books","Stationery","Printing","Photocopy","Lab materials","Online courses","Exam fees","College fees","Project expenses"],
"Travel":["Bus","Train","Auto","Uber/Ola","Rapido","Flight","Local travel","Travel to home","Travel during trips"],
"Personal":["Clothes","Shoes","Haircut","Skincare","Grooming","Accessories","Electronics","Mobile recharge","Internet"],
"Entertainment":["Movies","Games","Gaming purchases","OTT subscriptions","Events","Outings","Friends"],
"College Life":["Club expenses","Fests","College events","Hostel expenses","Room supplies","Laundry","Sports","Gym"],
"Other":["Medical","Emergency","Gifts","Donations","Miscellaneous"]
}
PAYMENTS=["UPI","Cash","Debit Card","Credit Card","Bank Transfer","Other"]
INCOME_CATEGORIES=["Money from Home","Scholarship","Part-time income","Internship income","Freelance income","Refund","Other"]

def month_name(y,m): return calendar.month_name[m]
def df_rows(rows): return pd.DataFrame([dict(r) for r in rows]) if rows else pd.DataFrame()
