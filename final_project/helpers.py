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

def getBar(start, end, accId = None):

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
          # Query DB
          totExpense = cur.execute("SELECT IFNULL(SUM(amount_cents/100) ,0) FROM transactions WHERE created_by_user_id = ? AND trans_type = ? and trans_date BETWEEN ? AND ?", (user["id"], TYPES[0],start, end,)).fetchone()[0]

          totIncome = cur.execute("SELECT IFNULL(SUM(amount_cents/100) ,0) FROM transactions WHERE created_by_user_id = ? AND trans_type = ? and trans_date BETWEEN ? AND ?", (user["id"], TYPES[1], start, end,)).fetchone()[0]

          con.close()

          # Generate & save bargraph
          fig, ax = plt.subplots()
          ax.bar(TYPES[1], totIncome)
          ax.bar(TYPES[0], totExpense)
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
     # Connect DB, get user and query database
     con = conDbDict()
     cur = con.cursor()
     user = getUser()

     if (not accId):
          data = cur.execute("SELECT trans_type, trans_date, SUM(amount_cents)/100 AS day_tot FROM transactions WHERE created_by_user_id = ? AND trans_date BETWEEN ? and ? GROUP BY trans_type, trans_date ORDER BY trans_date", (user["id"], start, end,)).fetchall()
          
          con.close()

     # accId passed through
     else:
          data = cur.execute("SELECT trans_type, trans_date, SUM(amount_cents)/100 AS day_tot FROM transactions WHERE created_by_user_id = ? AND account_id = ? AND trans_date BETWEEN ? and ? GROUP BY trans_type, trans_date ORDER BY trans_date", (user["id"], accId, start, end,)).fetchall()
          
          con.close()


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
     fig, ax = plt.subplots()
     ax.plot(expense_dates, expense_runtot, '-o')
     # ax.plot(income_dates, income_runtot, '-o')

     ax.xaxis.set_major_locator(mdates.DayLocator())      # one tick per day
     ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
     plt.savefig('static/my_line-expsnses.png') # Todo: Should probably add user id to name to allow multiple users 
     
     

     # Verify 
     if os.path.exists("static/my_line-expsnses.png"):
          return True
     else: 
          return False


def getPie(start, end, accId = None):


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
               transactions = cur.execute("SELECT amount_cents, account_id, category, id, trans_date, trans_type FROM transactions where created_by_user_id = ? ORDER BY trans_date DESC", (user["id"],)).fetchall()
          else:
               query = f"""SELECT amount_cents, account_id, category, trans_date, id, trans_type FROM transactions where created_by_user_id = ? ORDER BY trans_date DESC LIMIT {int(limit)}"""
        
               transactions = cur.execute(query, (user["id"],)).fetchall()

          con.close()
          return transactions
     
     else:

          if (limit == 0):
               transactions = cur.execute("SELECT amount_cents, account_id, category, id, trans_date, trans_type FROM transactions where created_by_user_id = ? AND acount_id = ? ORDER BY trans_date DESC", (user["id"], accId,)).fetchall()
          else:
               query = f"""SELECT amount_cents, account_id, category, trans_date, id, trans_type FROM transactions where created_by_user_id = ? AND account_id = ? ORDER BY trans_date DESC LIMIT {int(limit)}"""
        
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
     con = conDbDict()
     cur = con.cursor()

     user = cur.execute("SELECT id, username FROM users WHERE id = ?", (session["user_id"],)).fetchone()

     #case handeling
     match (accId, cat, trxType):
          # No Filters
          case (None, None, None):
               trxData = cur.execute("SELECT account_id, amount_cents, category, id, trans_date, trans_type FROM transactions where created_by_user_id = ? AND trans_date BETWEEN ? and ? ORDER BY trans_date", (user["id"], start, end,)).fetchall()

               con.close()
               return trxData
          
          # account only
          case (accId, None, None):
               trxData = cur.execute("SELECT account_id, amount_cents, category, id, trans_date, trans_type FROM transactions where created_by_user_id = ? AND account_id = ? AND trans_date BETWEEN ? and ? ORDER BY trans_date", (user["id"], accId, start, end,)).fetchall()

               con.close()
               return trxData

          # account & category
          case (accId, cat, None):
               trxData = cur.execute("SELECT account_id, amount_cents, category, id, trans_date, trans_type FROM transactions where created_by_user_id = ? AND account_id = ? AND category = ? AND trans_date BETWEEN ? and ? ORDER BY trans_date", (user["id"], accId, cat, start, end,)).fetchall()

               con.close()
               return trxData

          # account & trxType
          case (accId, None, trxType):
               trxData = cur.execute("SELECT account_id, amount_cents, category, id, trans_date, trans_type FROM transactions where created_by_user_id = ? AND account_id = ? AND trans_type = ? AND trans_date BETWEEN ? and ? ORDER BY trans_date", (user["id"], accId, trxType, start, end,)).fetchall()

               con.close()
               return trxData
          
          # account & category & trxType
          case (accId, cat, trxType):
               trxData = cur.execute("SELECT account_id, amount_cents, category, id, trans_date, trans_type FROM transactions where created_by_user_id = ? AND account_id = ? AND category = ? AND trans_type = ? AND trans_date BETWEEN ? and ? ORDER BY trans_date", (user["id"], accId, cat, trxType, start, end,)).fetchall()

               con.close()
               return trxData

          # category only
          case (None, cat, None):
               trxData = cur.execute("SELECT account_id, amount_cents, category, id, trans_date, trans_type FROM transactions where created_by_user_id = ? AND category = ? AND trans_date BETWEEN ? and ? ORDER BY trans_date", (user["id"], cat, start, end,)).fetchall()

               con.close()
               return trxData
               
          # category & trxType
          case (None, cat, trxType):
               trxData = cur.execute("SELECT account_id, amount_cents, category, id, trans_date, trans_type FROM transactions where created_by_user_id = ? AND category = ? AND trans_type = ? AND trans_date BETWEEN ? and ? ORDER BY trans_date", (user["id"], cat, trxType, start, end,)).fetchall()

               con.close()
               return trxData

          # trxType only
          case (None, None, trxType):
               trxData = cur.execute("SELECT account_id, amount_cents, category, id, trans_date, trans_type FROM transactions where created_by_user_id = ? AND trans_type = ? AND trans_date BETWEEN ? and ? ORDER BY trans_date", (user["id"], trxType, start, end,)).fetchall()

               con.close()
               return trxData