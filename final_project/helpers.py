import calendar
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from flask import session
import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import os
import sqlite3

TYPES = ["expense", "income"]
CATEGORIES = ["Food", "Insurance", "Salary"]

def conDbDict(db = "final.db"):
        # Connects to DB returns dicts
        con = sqlite3.connect(db)
        con.row_factory = sqlite3.Row
        return con

def getUser():
    con = conDbDict()
    cur = con.cursor()

    user = cur.execute("SELECT id, username FROM users WHERE id = ?", (session["user_id"],)).fetchone()

    con.close()
    return user

def getBar(start, end):
     con = conDbDict()
     cur = con.cursor()
     user = getUser()

     # Query DB
     totExpense = cur.execute("SELECT IFNULL(SUM(amount_cents) ,0) FROM transactions WHERE created_by_user_id = ? AND trans_type = ? and trans_date BETWEEN ? AND ?", (user["id"], TYPES[0],start, end,)).fetchone()[0]

     totIncome = cur.execute("SELECT IFNULL(SUM(amount_cents) ,0) FROM transactions WHERE created_by_user_id = ? AND trans_type = ? and trans_date BETWEEN ? AND ?", (user["id"], TYPES[1], start, end,)).fetchone()[0]



    # Generate & save bargraph
     plt.style.use('dark_background')
     fig, ax = plt.subplots()
     ax.bar(TYPES[1], totIncome)
     ax.bar(TYPES[0], totExpense)
     plt.savefig('static/my_bar_expesne_vs_income.png')

     con.close()
     # Verify
     if os.path.exists('static/my_bar_expesne_vs_income.png'):
          return True
     else:
          return False

def getLine(start, end):
        # Connect DB, get user and query database
        con = conDbDict()
        cur = con.cursor()
        user = getUser()

        data = cur.execute("SELECT trans_type, trans_date, SUM(amount_cents) AS day_tot FROM transactions WHERE created_by_user_id = ? AND trans_date BETWEEN ? and ? GROUP BY trans_type, trans_date ORDER BY trans_date", (user["id"], start, end,)).fetchall()

        # Expense vars 
        expense_dates = []
        expense_runtot = []
        expnse_cumsum = 0

        for i in data:
            # Append expense data to expense vars
            if (i["trans_type"] == TYPES[0]):
                try:
                    dt = datetime.fromisoformat(i["trans_date"])
                except:
                    dt = datetime.strptime(i["trans_date"], "%Y-%m-%d")
                expense_dates.append(dt)
                expnse_cumsum += i["day_tot"]
                expense_runtot.append(expnse_cumsum)

        # Plot and save graph
        plt.style.use('dark_background')
        fig, ax = plt.subplots()
        ax.plot(expense_dates, expense_runtot, '-o')
        # ax.plot(income_dates, income_runtot, '-o')
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
        plt.savefig('static/my_line-expsnses.png') # Todo: Should probably add user id to name to allow multiple users 
       
        con.close()

       # Verify 
        if os.path.exists("static/my_line-expsnses.png"):
            return True
        else: 
             return False

def getPie(start, end):
     con = conDbDict()
     cur = con.cursor()
     user = getUser()

     data = cur.execute("SELECT category, sum(amount_cents) as totals FROM transactions WHERE created_by_user_id = ? AND trans_type = ? AND trans_date BETWEEN ? AND ? GROUP BY category ORDER BY totals", (user["id"], TYPES[0], start, end,)).fetchall()

     categories = []
     totals = []

     for i in data:
          categories.append(i["category"])
          totals.append(i["totals"])

     #plt.style.use('dark_background')
     fig, ax = plt.subplots()
     # ax.pie(totals, labels=categories, autopct='%1.1f%%')

     def autopct_func(pct, allvals):
          absolute = round(pct / 100 * sum(allvals), 2)
          return f"{pct:.1f}%\n({absolute})"
     
     wedges, texts, autotexts = ax.pie(
          totals,
          labels=categories,
          autopct=lambda pct: autopct_func(pct, totals), 
          wedgeprops={'width': 0.4},
          startangle=90

     )

     ax.legend(
          wedges, categories,
          title="Categories",
          loc="center left",
          bbox_to_anchor=(1, 0, 0.5, 1)
     )

     plt.setp(autotexts, size=8, weight="bold")
     ax.set_aspect('equal')

     ax.set_title("Spend by Category")

     plt.savefig('static/my_pie_expenses.png')
     plt.close(fig)


     con.close()
     if os.path.exists('static/my_pie_expenses.png'):
          return True
     else:
          return False

def getTrans(limit = 0):
    con = conDbDict()
    cur = con.cursor()

    user = getUser()

    if (limit == 0):
        transactions = cur.execute("SELECT amount_cents, category, trans_date, trans_type FROM transactions where created_by_user_id = ? ORDER BY trans_date", (user["id"],)).fetchall()
    else:
        query = f"""SELECT amount_cents, category, trans_date, trans_type FROM transactions where created_by_user_id = ? ORDER BY trans_date LIMIT {int(limit)}
        """

        transactions = cur.execute(query, (user["id"], )).fetchall()

    con.close()
    return transactions
         


     
