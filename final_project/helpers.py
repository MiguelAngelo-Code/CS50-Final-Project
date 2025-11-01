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

def getLine(start, end):
        con = conDbDict()
        cur = con.cursor()
        user = getUser()

        # Line Graph: Expense & income over time
        data = cur.execute("SELECT type, date, SUM(amount) AS day_tot FROM transactions WHERE user_id = ? AND date BETWEEN ? and ? GROUP BY type, date ORDER BY date", (user["id"], start, end,)).fetchall()

        # Expense vars 
        expense_dates = []
        expense_runtot = []
        expnse_cumsum = 0
        # Income vars not in use
        income_dates = []
        income_runtot = []
        income_cumsum = 0

        for i in data:
            # Append expense data to expense vars
            if (i["type"] == "Expense"):
                try:
                    dt = datetime.fromisoformat(i["date"])
                except:
                    dt = datetime.strptime(i["dates"], "%Y-%m-%d")
                expense_dates.append(dt)
                expnse_cumsum += i["day_tot"]
                expense_runtot.append(expnse_cumsum)
            # Appends incone data to income vars curentlty not in use as. not sure about this function
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
       
        if os.path.exists("static/my_line-expsnses.png"):
            return True
        else: 
             return False
