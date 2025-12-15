import calendar
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from flask import session
import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import numpy as np
import os
import sqlite3

TYPES = ["expense", "income"]

def conDbDict(db = "final.db"):
        # Connects to DB returns dicts
        con = sqlite3.connect(db)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys = ON")
        
        return con

def getAccounts():

     con = conDbDict()
     cur = con.cursor()

     user = getUser()

     accounts = cur.execute("SELECT account_name, balance_cents, id FROM accounts WHERE user_id = ?", (user["id"],)).fetchall()

     con.close()

     return accounts

def getCats():

     con = conDbDict()
     cur = con.cursor()

     user = getUser()

     categories = cur.execute("SELECT name, id FROM categories WHERE user_id = ?", (user["id"],)).fetchall()

     con.close()

     return categories

def getBar(start = None, end = None, accId = None):
     
     # Build WHERE clause & query 
     where, params = buildWhereClauseTrx(start, end, accId)

     query = f"SELECT trans_type, IFNULL(SUM(amount_cents/100) ,0) AS total FROM transactions {where} GROUP BY trans_type"

     # Execute query
     con = conDbDict()
     cur = con.cursor()

     trxData = cur.execute(query, params).fetchall()
     con.close()

     totIncome = 0.00

     totExpense = 0.00

     for i in trxData:
          if i["trans_type"] == "income":
               totIncome = i["total"]
          if i["trans_type"] == "expense":
               totExpense = i["total"]


     # Styling
     plt.rcParams.update({
     "figure.facecolor": "#0f0f11",      # page background
     "axes.facecolor":   "#18181c",      # plot background
     "axes.edgecolor":   "#3a3a46",
     "axes.labelcolor":  "#f5f5f7",
     "xtick.color":      "#b3b3c3",
     "ytick.color":      "#b3b3c3",
     "text.color":       "#f5f5f7",
     "axes.grid":        True,
     "grid.color":       "#2a2a33",
     "grid.linestyle":   "--",
     "grid.linewidth":   0.5,
     "figure.autolayout": True
     })

     # Generate & save bargraph
     plt.style.use('dark_background')
     fig, ax = plt.subplots()
     ax.bar("Income", totIncome)
     ax.bar("Expense", totExpense)
     plt.savefig('static/my_bar_expesne_vs_income.png')

     # Verify
     if os.path.exists('static/my_bar_expesne_vs_income.png'):
          return True
     else:
          return False
          

     
     con = conDbDict()
     cur = con.cursor()
     user = getUser()

     if (not accId):
          # Query DB
          totExpense = cur.execute("SELECT IFNULL(SUM(amount_cents/100) ,0) FROM transactions WHERE created_by_user_id = ? AND trans_type = ? and trans_date BETWEEN ? AND ?", (user["id"], TYPES[0],start, end,)).fetchone()[0]

          totIncome = cur.execute("SELECT IFNULL(SUM(amount_cents/100) ,0) FROM transactions WHERE created_by_user_id = ? AND trans_type = ? and trans_date BETWEEN ? AND ?", (user["id"], TYPES[1], start, end,)).fetchone()[0]

          con.close()

          # Generate & save bargraph
          fig, ax = plt.subplots()
          ax.barh(TYPES[1], totIncome)
          ax.barh(TYPES[0], totExpense)
          plt.savefig('static/my_bar_expesne_vs_income.png')

          # Verify
          if os.path.exists('static/my_bar_expesne_vs_income.png'):
               return True
          else:
               return False
     
     else:
 
          # Query DB
          totExpense = cur.execute("SELECT IFNULL(SUM(amount_cents/100) ,0) FROM transactions WHERE created_by_user_id = ? AND account_id = ? AND trans_type = ? and trans_date BETWEEN ? AND ?", (user["id"], accId, TYPES[0],start, end,)).fetchone()[0]

          totIncome = cur.execute("SELECT IFNULL(SUM(amount_cents/100) ,0) FROM transactions WHERE created_by_user_id = ? AND account_id = ? AND trans_type = ? and trans_date BETWEEN ? AND ?", (user["id"], accId, TYPES[1], start, end,)).fetchone()[0]

          con.close()

          # Generate & save bargraph
          plt.style.use('dark_background')
          fig, ax = plt.subplots()
          ax.bar(TYPES[1], totIncome)
          ax.bar(TYPES[0], totExpense)
          plt.savefig('static/my_bar_expesne_vs_income.png')

          # Verify
          if os.path.exists('static/my_bar_expesne_vs_income.png'):
               return True
          else:
               return False

def getLine(start, end, accId = None):

     # Build WHERE clause
     where, params = buildWhereClauseTrx(start, end, accId)

     query = f"SELECT trans_type, trans_date, SUM(amount_cents)/100 AS day_tot FROM transactions {where} GROUP BY trans_type, trans_date ORDER BY trans_date"

     # Execute query
     con = conDbDict()
     cur = con.cursor()

     data = cur.execute(query, params).fetchall()
     con.close()

     # Expense vars 
     expense_dates = []
     expense_runtot = []
     expnse_cumsum = 0

     for i in data:
          # Append expense data to expense vars
          if (i["trans_type"] == "expense"):
               try:
                    dt = datetime.fromisoformat(i["trans_date"])
               except:
                    dt = datetime.strptime(i["trans_date"], "%Y-%m-%d")

               expense_dates.append(dt)
               expnse_cumsum += i["day_tot"]
               expense_runtot.append(expnse_cumsum)

     # Stylig
     plt.rcParams.update({
          "figure.facecolor": "#0f0f11",      # page background
          "axes.facecolor":   "#18181c",      # plot background
          "axes.edgecolor":   "#3a3a46",
          "axes.labelcolor":  "#f5f5f7",
          "xtick.color":      "#b3b3c3",
          "ytick.color":      "#b3b3c3",
          "text.color":       "#f5f5f7",
          "axes.grid":        True,
          "grid.color":       "#2a2a33",
          "grid.linestyle":   "--",
          "grid.linewidth":   0.5,
          "figure.autolayout": True
     })

     # Plot and save graph
     fig, ax = plt.subplots()
     ax.plot(expense_dates, expense_runtot, '-o')

     ax.xaxis.set_major_locator(mdates.DayLocator())      
     ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
     plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

     plt.savefig('static/my_line-expsnses.png') 
     
     # Verify 
     if os.path.exists("static/my_line-expsnses.png"):
          return True
     else: 
          return False


def getPie(start, end, accId = None):

     # Build WHERE clause
     where, params = buildWhereClauseTrx(start, end, accId)

     query = f"SELECT category, SUM(amount_cents) AS totals FROM transactions {where} and trans_type = 'expense' GROUP BY category ORDER BY totals"

     # Execute query
     con = conDbDict()
     cur = con.cursor()

     data = cur.execute(query, params).fetchall()
     con.close()

     # Creat list of categoreis and totals to plot
     categories = []
     totals = []

     for i in data:
          categories.append(i["category"])
          totals.append(round(i["totals"] / 100.0, 2))

     # Styling
     plt.rcParams.update({
          "figure.facecolor": "#0f0f11",      # page background
          "axes.facecolor":   "#18181c",      # plot background
          "axes.edgecolor":   "#3a3a46",
          "axes.labelcolor":  "#f5f5f7",
          "xtick.color":      "#b3b3c3",
          "ytick.color":      "#b3b3c3",
          "text.color":       "#f5f5f7",
          "axes.grid":        True,
          "grid.color":       "#2a2a33",
          "grid.linestyle":   "--",
          "grid.linewidth":   0.5,
          "figure.autolayout": True
     })

     # Generate chart
     #plt.style.use('dark_background')
     fig, ax = plt.subplots()
     # ax.pie(totals, labels=categories, autopct='%1.1f%%')

     def autopct_func(pct, allvals):
          absolute = round(pct / 100 * sum(allvals), 2)
          return f"{pct:.0f}%\n({absolute:.2f})"
     
     

     # Draw the donut chart (no labels inside here)
     wedges, texts, autotexts = ax.pie(
          totals,
          labels=None,                               # we add category labels manually
          autopct=lambda pct: autopct_func(pct, totals),
          pctdistance=0.8,                            # move percent numbers inward
          wedgeprops={'width': 0.4},
          startangle=90
     )

     # Improve readability of the percentage + amount inside the donut
     for t in autotexts:
          t.set_fontsize(10)
          t.set_weight('bold')
          # Add outline to text so it stays readable over any color
          t.set_path_effects([
               path_effects.Stroke(linewidth=2, foreground='black'),
               path_effects.Normal()
          ])

     # Add category labels *outside* the donut
     for i, wedge in enumerate(wedges):
          angle = (wedge.theta2 + wedge.theta1) / 2
          x = 1.25 * np.cos(np.deg2rad(angle))
          y = 1.25 * np.sin(np.deg2rad(angle))
          ax.text(
               x, y,
               categories[i],
               ha='center', va='center',
               fontsize=12,
               color="white",
               weight="bold"
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

     if os.path.exists('static/my_pie_expenses.png'):
          return True
     else:
          return False
     #old code


     plt.rcParams.update({
          "figure.facecolor": "#0f0f11",      # page background
          "axes.facecolor":   "#18181c",      # plot background
          "axes.edgecolor":   "#3a3a46",
          "axes.labelcolor":  "#f5f5f7",
          "xtick.color":      "#b3b3c3",
          "ytick.color":      "#b3b3c3",
          "text.color":       "#f5f5f7",
          "axes.grid":        True,
          "grid.color":       "#2a2a33",
          "grid.linestyle":   "--",
          "grid.linewidth":   0.5,
          "figure.autolayout": True
     })

     con = conDbDict()
     cur = con.cursor()
     user = getUser()

     if (not accId):
          data = cur.execute("SELECT category, SUM(amount_cents) AS totals FROM transactions WHERE created_by_user_id = ? AND trans_type = ? AND trans_date BETWEEN ? AND ? GROUP BY category ORDER BY totals", (user["id"], TYPES[0], start, end,)).fetchall()

          con.close()

     else:
          data = cur.execute("SELECT category, sum(amount_cents) as totals FROM transactions WHERE created_by_user_id = ? AND account_id = ? AND trans_type = ? AND trans_date BETWEEN ? AND ? GROUP BY category ORDER BY totals", (user["id"], accId, TYPES[0], start, end,)).fetchall()

          con.close()

     categories = []
     totals = []

     for i in data:
          categories.append(i["category"])
          totals.append(round(i["totals"] / 100.0, 2))

     #plt.style.use('dark_background')
     fig, ax = plt.subplots()
     # ax.pie(totals, labels=categories, autopct='%1.1f%%')

     def autopct_func(pct, allvals):
          absolute = round(pct / 100 * sum(allvals), 2)
          return f"{pct:.0f}%\n({absolute:.2f})"
     
     

     # Draw the donut chart (no labels inside here)
     wedges, texts, autotexts = ax.pie(
          totals,
          labels=None,                               # we add category labels manually
          autopct=lambda pct: autopct_func(pct, totals),
          pctdistance=0.8,                            # move percent numbers inward
          wedgeprops={'width': 0.4},
          startangle=90
     )

     # Improve readability of the percentage + amount inside the donut
     for t in autotexts:
          t.set_fontsize(10)
          t.set_weight('bold')
          # Add outline to text so it stays readable over any color
          t.set_path_effects([
               path_effects.Stroke(linewidth=2, foreground='black'),
               path_effects.Normal()
          ])

     # Add category labels *outside* the donut
     for i, wedge in enumerate(wedges):
          angle = (wedge.theta2 + wedge.theta1) / 2
          x = 1.25 * np.cos(np.deg2rad(angle))
          y = 1.25 * np.sin(np.deg2rad(angle))
          ax.text(
               x, y,
               categories[i],
               ha='center', va='center',
               fontsize=12,
               color="white",
               weight="bold"
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

     if os.path.exists('static/my_pie_expenses.png'):
          return True
     else:
          return False


def getTrans(limit = 0, accId = None):
     con = conDbDict()
     cur = con.cursor()

     user = getUser()

     if (not accId):
     
          if (limit == 0):
               transactions = cur.execute("SELECT printf('%.2f', amount_cents / 100.0) AS amount_cents, account_id, category, id, trans_date, trans_type FROM transactions where created_by_user_id = ? ORDER BY trans_date DESC", (user["id"],)).fetchall()
          else:
               query = f"""SELECT printf('%.2f', amount_cents / 100.0) AS amount_cents, account_id, category, trans_date, id, trans_type FROM transactions where created_by_user_id = ? ORDER BY trans_date DESC LIMIT {int(limit)}"""
        
               transactions = cur.execute(query, (user["id"],)).fetchall()

          con.close()
          return transactions
     
     else:

          if (limit == 0):
               transactions = cur.execute("SELECT printf('%.2f', amount_cents / 100.0) AS amount_cents, account_id, category, id, trans_date, trans_type FROM transactions where created_by_user_id = ? AND acount_id = ? ORDER BY trans_date DESC", (user["id"], accId,)).fetchall()
          else:
               query = f"""SELECT printf('%.2f', amount_cents / 100.0) AS amount_cents, account_id, category, trans_date, id, trans_type FROM transactions where created_by_user_id = ? AND account_id = ? ORDER BY trans_date DESC LIMIT {int(limit)}"""
        
               transactions = cur.execute(query, (user["id"], accId,)).fetchall()

          con.close()
          return transactions
     
def getTransDate(start, end):
     
     user = getUser()

     con = conDbDict()
     cur = con.cursor()
     
     transactions = cur.execute("SELECT account_id, amount_cents, category, id, trans_date, trans_type FROM transactions where created_by_user_id = ? AND trans_date BETWEEN ? and ? ORDER BY trans_date", (user["id"], start, end,)).fetchall()

     con.close()
     
     return transactions     

def getUser():
    con = conDbDict()
    cur = con.cursor()

    user = cur.execute("SELECT id, username FROM users WHERE id = ?", (session["user_id"],)).fetchone()

    con.close()

    return user
     
def getTrxData(start, end, accId = None, cat = None, trxType = None):

     where, params = buildWhereClauseTrx(start, end, accId, cat, trxType)

     # Execute query
     con = conDbDict()
     cur = con.cursor()

     query = f"SELECT account_id, printf('%.2f', amount_cents / 100.0) AS amount_cents, category, id, trans_date, trans_type FROM transactions {where} ORDER BY trans_date DESC"
     trxData = cur.execute(query, params).fetchall()

     con.close()
     return trxData


def buildWhereClauseTrx(start = None, end = None, accId = None, cat = None, trxType = None):

     # Normalise empty strings
     start = start if start else None
     end = end if end else None
     accId =  accId if accId else None
     cat = cat if cat else None
     trxType = trxType if trxType else None

     # Get user_id
     user = getUser()
     user_id = user["id"]

     # Build WHERE clause
     where = "WHERE created_by_user_id = ?"
     params = [user_id]

     if (start and end):
          where += " AND trans_date BETWEEN ? AND ?"
          params.append(start)
          params.append(end)
     elif (start and not end):
          where += " AND trans_date = ?"
          params.append(start)
     elif (end and not start):
          where += " AND trans_date = ?"
          params.append(end)

     if (accId):
          where += " AND account_id = ?"
          params.append(accId)
     if (cat):
          where += " AND category = ?"
          params.append(cat)
     if (trxType):
          where += " AND trans_type = ?"
          params.append(trxType)

     return where, params