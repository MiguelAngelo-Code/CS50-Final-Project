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

TYPES = ["Expense", "Income"]
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
     totExpense = float(cur.execute("SELECT SUM(amount) FROM transactions WHERE user_id = ? AND type = ? and date BETWEEN ? AND ?", (user["id"], TYPES[0],start, end,)).fetchone()[0])

     totIncome = float(cur.execute("SELECT SUM(amount) FROM transactions WHERE user_id = ? AND type = ? and date BETWEEN ? AND ?", (user["id"], TYPES[1], start, end,)).fetchone()[0])

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

        data = cur.execute("SELECT type, date, SUM(amount) AS day_tot FROM transactions WHERE user_id = ? AND date BETWEEN ? and ? GROUP BY type, date ORDER BY date", (user["id"], start, end,)).fetchall()

        # Expense vars 
        expense_dates = []
        expense_runtot = []
        expnse_cumsum = 0
        # Income vars
        income_dates = []
        income_runtot = []
        income_cumsum = 0

        for i in data:
            # Append expense data to expense vars
            if (i["type"] == TYPES[0]):
                try:
                    dt = datetime.fromisoformat(i["date"])
                except:
                    dt = datetime.strptime(i["dates"], "%Y-%m-%d")
                expense_dates.append(dt)
                expnse_cumsum += i["day_tot"]
                expense_runtot.append(expnse_cumsum)
            # Appends incone data to income vars
            else:
                try:
                    dt = datetime.fromisoformat(i["date"])
                except:
                    dt = datetime.strptime(i["dates"], "%Y-%m-%d")
                income_dates.append(dt)
                income_cumsum += i["day_tot"]
                income_runtot.append(income_cumsum)

        # Plot and save graph
        plt.style.use('dark_background')
        fig, ax = plt.subplots()
        ax.plot(expense_dates, expense_runtot, '-o')
        ax.plot(income_dates, income_runtot, '-o')
        #ax = plt.gca()
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

     data = cur.execute("SELECT category, sum(amount) as totals FROM transactions WHERE user_id = ? AND type = ? AND date BETWEEN ? AND ? GROUP BY category ORDER BY totals", (user["id"], TYPES[0], start, end,)).fetchall()

     categories = []
     totals = []

     for i in data:
          categories.append(i["category"])
          totals.append(i["totals"])

     #plt.style.use('dark_background')
     fig, ax = plt.subplots()
     ax.pie(totals, labels=categories, autopct='%1.1f%%')
     plt.savefig('static/my_pie_expenses.png')

     con.close()
     if os.path.exists('static/my_pie_expenses.png'):
          return True
     else:
          return False

          
     
