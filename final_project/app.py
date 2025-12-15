import io
import calendar
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from decimal import Decimal, ROUND_HALF_UP
from flask import Flask, flash, redirect, render_template, Response, request, session
from flask_session import Session
from helpers import conDbDict, getAccounts, getCats, getBar, getLine, getPie, getTrans, getTransDate, getTrxData, getUser
import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

# Configure application
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = "some-secret-key"

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Constants
TYPES = ["expense", "income"]


# Index: Dashboard
@app.route("/", methods=["GET", "POST"])
def index():
    # Checks user is loged in
    if ("user_id" not in session):
        return redirect("/login")
    
    return redirect("/get_charts")


# Add functions
@app.route("/add_account", methods=["POST"])
def add_account():

    # Request new user input
    newAccount = request.form.get("account_name")

    # Connect DB & get user
    con = conDbDict()
    cur = con.cursor()

    user = getUser()

    # Check unique account name
    accounts = cur.execute("SELECT account_name FROM accounts WHERE user_id = ?", (user["id"], )).fetchall()
    account_names = [row["account_name"] for row in accounts]

    if newAccount in account_names:
        return render_template("error.html", message="Account name already exists")
    
    # Update DB
    try:
        cur.execute("INSERT INTO accounts (account_name, user_id) VALUES (?, ?)", (newAccount, user["id"], ))
        con.commit()
        con.close()
    except:
        con.close()
        return render_template("/error.html", message="Unable to add account")

    return redirect("/manage_accounts")

@app.route("/add_cat", methods=["POST"]) 
def add_cat():

    # Connect DB & get user
    con = conDbDict()
    cur = con.cursor()

    user = getUser()

    # Request user input & categories from DB
    newCat = request.form.get("new_cat")

    categories = cur.execute("SELECT name FROM categories WHERE user_id = ?", (user["id"],)).fetchall()
    categoryNames = [row["name"] for row in categories]

    if (newCat in categoryNames):
        # Close connection retrn error
        con.close()
        return render_template("error.html", message="already in categories")
    else:
        # Insert into DB 
        cur.execute("INSERT INTO categories (name, user_id) values (?, ?)", (newCat, user["id"],))
        con.commit()
        # Close connection and redirect to index
        con.close()

    return redirect(request.referrer or "/manage_accounts")
    
@app.route("/add_transaction", methods=["GET", "POST"])
def add_transaction():
    if ("user_id" not in session):
        return redirect("/login")
    
    if (request.method == "GET"):
        # Connect DB & get user ID
        con = conDbDict()
        cur = con.cursor()

        user = getUser()

        # Fetch user transaction & categories
        transactions = getTrans()

        categories = cur.execute("SELECT name FROM categories WHERE user_id = ?", (user["id"],)).fetchall()

        # Get user Accounts
        accounts = cur.execute("SELECT account_name, balance_cents, id FROM accounts WHERE user_id = ?", (user["id"],)).fetchall()
               
        # Render index
        con.close()

        return render_template("add_transaction.html", accounts=accounts, user=user, types=TYPES, categories=categories, transactions=transactions)
    
    # Insert transaction into database
    else:
        # Connect DB & get user ID
        con = conDbDict()
        cur = con.cursor()

        user = getUser()

        # Request user input
        account = request.form.get("account")
        amount = Decimal(request.form.get("amount")).quantize(Decimal("0.01"), ROUND_HALF_UP)
        amount_cents = int (amount * 100)
        category = request.form.get("category")
        date = request.form.get("date")
        trans_type = request.form.get("type")

        #Check TYPES
        if (trans_type not in TYPES):
                return render_template("error.html", message="invalid type submission")
        
        # Insert into DB, close connection & redirect
        cur.execute("INSERT INTO transactions (account_id, amount_cents, category, created_by_user_id, trans_date, trans_type) values (?, ?, ?, ?, ?, ?)", (account, amount_cents, category, user["id"], date, trans_type,))
        con.commit()

        con.close()

        return redirect(request.referrer or "/manage_transactions")


# Delete functions
@app.route("/delete_account", methods=["POST"])
def delete_account():
    accountId = request.form.get("delete-account")

    con = conDbDict()
    cur = con.cursor()

    cur.execute("DELETE FROM accounts WHERE id = ?", (accountId,))
    con.commit()
    con.close()

    return redirect("/manage_accounts")

@app.route("/delete_category", methods=["POST"])
def delete_category():
    categoryId = request.form.get("delete-cat")

    con = conDbDict()
    cur = con.cursor()

    try:
        cur.execute("DELETE FROM categories WHERE id = ?", (categoryId,))
        con.commit()
        con.close()
    except:
        con.close()
        return render_template("/error.html", message="Error: Could not delete account")
    
    return redirect("/manage_accounts")

@app.route("/delete_transaction", methods=["POST"])
def delete_transaction():

    transId = request.form.get("deleteTrans")

    con = conDbDict()
    cur = con.cursor()

    cur.execute("DELETE FROM transactions WHERE id = ?", (transId,))
    con.commit()
    con.close()

    return redirect("/manage_transactions")


# Edit functions
@app.route("/edit_account", methods=["POST"])
def edit_account():

    # Get user input
    accountName = request.form.get("account_name")
    accountId = request.form.get("id")

    # Connect DB
    con = conDbDict()
    cur = con.cursor()

    # Updates DB
    try:
        cur.execute("UPDATE accounts SET account_name = ? WHERE id = ?", (accountName, accountId, ))
        con.commit()
        con.close()
    except:
        con.close()
        return render_template("/error.html", message="Not able to edit account name")
    
    # Redirect
    return redirect("/manage_accounts")

@app.route("/edit_category", methods=["POST"])
def edit_category():
    # Get user input
    categoryName = request.form.get("cat_name")
    categoryId = request.form.get("id")

    # Connect DB
    con = conDbDict()
    cur = con.cursor()

    # Updates DB
    try:
        cur.execute("UPDATE categories SET name = ? WHERE id = ?", (categoryName, categoryId,))
        con.commit()
        con.close()
    except:
        con.close()
        return render_template("/error.html", message="Not able to edit category name")
    
    # Redirect
    return redirect("/manage_accounts")

@app.route("/edit_transactions", methods=["POST"])
def edit_transactions():

    # Get user inputs
    transId = request.form.get("id")
    account = request.form.get("account")
    transType = request.form.get("type")
    category = request.form.get("category")
    date = request.form.get("date")

    amount = Decimal(request.form.get("amount")).quantize(Decimal("0.01"), ROUND_HALF_UP)
    amount_cents = int (amount * 100)
    # Connect DB
    con = conDbDict()
    cur = con.cursor()

    # Updates DB
    try:
        cur.execute("UPDATE transactions SET account_id = ?, trans_type = ?, category = ?, trans_date = ?, amount_cents = ? WHERE id = ?", (account, transType, category, date, amount_cents, transId, ))
        con.commit()
        con.close()
    except:
        con.close()
        return render_template("/error.html", message="Not able to edit transaction")

    # Redirect
    return redirect("/manage_transactions")


# Generate Charts
@app.route("/get_charts", methods=["GET", "POST"])
def get_charts():

    # Get user and user categories
    user = getUser()
    categories = getCats()

    # Get user Accounts
    con = conDbDict()
    cur = con.cursor()

    accounts = cur.execute("SELECT account_name, printf('%.2f', balance_cents / 100.0) AS balance, id FROM accounts WHERE user_id = ?", (user["id"],)).fetchall()

    con.close()

    # Generates defualt graphes based on current month
    if (request.method == "GET"):

        # Set start and end dates as first and last day of current month
        current_date = date.today()
        start = current_date + relativedelta(day=1)
        end = current_date + relativedelta(day=31)

        print(f"CONSOL DEBUG: start: {start}, end: {end}")

        startM = start.strftime("%B")
        startY = start.strftime("%Y") 

        # Line Graph: Expenses
        try:
            getLine(start, end)
        except:
            return render_template("error.html", message="Error with line graph")
        
        # Bar graph: Expense vs income
        try:
            getBar(start, end)
        except:
            return render_template("error.html", message="Error with bar graph")
        
        # Pie chart: Spend by category
        try:
            getPie(start, end)
        except:
            return render_template("error.html", message="Error with pie graph")


        # Fetch user transaction
        transactions = getTrxData(start, end)

        searchedAcc = accounts

        dashM = f"Your Dashboard for {startM} {startY}"

        return render_template("index.html", accounts=accounts, categories=categories, dashM=dashM, bar="static/my_bar_expesne_vs_income.png", chart="static/my_line-expsnses.png", pie="static/my_pie_expenses.png", searchedAcc=searchedAcc, transactions=transactions, types=TYPES, user=user)
    
    
    # Generates Graphes based on filters
    else:

        # Request user filters & standardise empty fields to None
        account = request.form.get("filter-account-id")
        if (account == ""):
            account = None

        start = request.form.get("filter-start")
        if (start == ""):
            start = None
        else:
            try:
                start = date.fromisoformat(start)
            except:
                start = date.strptime(start, "%Y-%m-%d")
                
        end = request.form.get("filter-end")
        # No user input - Set defualt date
        if (end == ""):
            end = None
        else:
            try:
                end = date.fromisoformat(end)
            except:
                end = date.strptime(end, "%Y-%m-%d")


        # Checks start is before end and set messaging
        if(start and end):
            if (start > end):
                flash("Error: Please end date must be after start date")
                return redirect("/")
            
            dashM = f"Your Dashboard for {start.strftime("%d/%m/%Y")} to {end.strftime("%d/%m/%Y")}"

        elif (start and not end):
            dashM = f"Your Dashboard for transactions on {start.strftime("%d/%m/%Y")}"

        elif (end and not start):
            dashM = f"Your Dashboard for transactions on {end.strftime("%d/%m/%Y")}"

        elif (not start and not end): 
            dashM = f"Your Dashboard for all transactions"

         
        # Generate Charts
        try:
            getLine(start, end, account)
        except:
            return render_template("error.html", message="Error with line graph")
        
        getBar(start, end)
        try:
            getBar(start, end, account)
        except:
            return render_template("error.html", message="Error with bar graph")

        try:
            getPie(start, end, account)
        except:
            return render_template("error.html", message="Error with pie graph")
        
        # Query DB for transactions and accounts
        transactions = getTrxData(start, end, account)

        con = conDbDict()
        cur = con.cursor()

        searchedAcc = cur.execute("SELECT account_name, printf('%.2f', balance_cents / 100.0) balance, id FROM accounts WHERE user_id = ? and id = ?", (user["id"], account)).fetchall()

        con.close()

        return render_template("index.html", accounts=accounts, categories=categories, bar="static/my_bar_expesne_vs_income.png", chart="static/my_line-expsnses.png", dashM=dashM, pie="static/my_pie_expenses.png", start=start, end=end, searchedAcc=searchedAcc, transactions=transactions, types=TYPES, user=user)

        # Match case based on filter options
        match (account):

            # No Filters - Date only
            case (None):
                try:
                    getLine(start, end)
                except:
                    return render_template("error.html", message="Error with line graph")
                
                try:
                    getBar(start, end)
                except:
                    return render_template("error.html", message="Error with bar graph")

                try:
                    getPie(start, end)
                except:
                    return render_template("error.html", message="Error with pie graph")
                
                # Query DB for 5 most recent transactions  
                transactions = getTrxData(start, end)

                searchedAcc = accounts

                return render_template("index.html", accounts=accounts, categories=categories, bar="static/my_bar_expesne_vs_income.png", chart="static/my_line-expsnses.png", month_name=month_name, month_year=month_year, pie="static/my_pie_expenses.png", start=start, end=end, searchedAcc=searchedAcc, transactions=transactions, types=TYPES, user=user)
            
            # Account filtered
            case (account):
                
                try:
                    getBar(start, end, account)
                except:
                    return render_template("error.html", message="Error with bar graph")
                
                try:
                    getLine(start, end, account)
                except:
                    return render_template("error.html", message="Error with line graph")
                
                try:
                    getPie(start, end, account)
                except:
                    return render_template("error.html", message="Error with pie graph")
                        
                transactions = getTrxData(start, end, account)

                con = conDbDict()
                cur = con.cursor()

                searchedAcc = cur.execute("SELECT account_name, balance_cents/100 AS balance, id FROM accounts WHERE user_id = ? and id = ?", (user["id"], account)).fetchall()

                con.close()

                return render_template("index.html", accounts=accounts, categories=categories, bar="static/my_bar_expesne_vs_income.png", chart="static/my_line-expsnses.png", month_name=month_name, month_year=month_year, pie="static/my_pie_expenses.png", start=start, end=end, searchedAcc=searchedAcc, transactions=transactions, types=TYPES, user=user)


# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if (request.method == "POST"):

        # Get username and password 
        username = request.form.get("username")
        password = request.form.get("password")

        #Todo: make sure check is agnostic of case
        # Check inputs
        if (not username or not password):
            return render_template("error.html", message="invalid input")

        # Connect DB
        con = conDbDict()
        cur = con.cursor()

        # Get user id & hash using lowercase username
        user = cur.execute("SELECT id, hash FROM users WHERE username = ?", (username,)).fetchall()

        # Check username
        if (not user):
            con.close()
            return render_template("error.html", message="user not found")
        # Check password
        if (check_password_hash(user[0]["hash"], password) == False):
            con.close()
            return render_template("error.html", message="Invalid Password")
        
        # Login 
        session["user_id"] = user[0]["id"]

        # Todo: redirect to /index
        con.close()
        return redirect("/")
        
    else: 
        return render_template("login.html")


# Logout
@app.route("/logout")
def logout():

    # Logout user
    session.clear()

    #redirect to index
    return redirect("/")


# Render mangement pages
@app.route("/manage_accounts", methods = ["GET", "POST"])
def manage_accounts():
    
    if (request.method == "GET"):

        accounts = getAccounts()
        categories = getCats()

        return render_template("/manage_accounts.html", accounts=accounts, categories=categories)

@app.route("/manage_transactions", methods = ["GET", "POST"])
def manage_transactions():

    user = getUser()
    con = conDbDict()
    cur = con.cursor()

    accounts = cur.execute("SELECT account_name, balance_cents, id FROM accounts WHERE user_id = ?", (user["id"],)).fetchall()
    categories = cur.execute("SELECT name FROM categories WHERE user_id = ?", (user["id"],)).fetchall()

    con.close()

    if (request.method == "GET"):

        # Set start and end dates as first and last day of current month
        # Todo: this code is repeated fit whole transaction date setting into helper function
        
        trasactions = getTrans()

        return render_template("manage_transactions.html", accounts=accounts, categories=categories, transactions=trasactions, types=TYPES)
    
    else:

        # Request user filters & set empty fields to None
        account = request.form.get("filter-account-id")
        if (account == ""):
            account = None

        category = request.form.get("filter-category")
        if (category == ""):
            category = None

        trxType = request.form.get("filter-type")
        if (trxType == ""):
            trxType = None

        # Request date filters, apply curent month start and end date if date fields empty
        start = request.form.get("filter-start")
        if (start == ""):
            start = None
        else:
            try:
                start = date.fromisoformat(start)
            except:
                start = date.strptime(start, "%Y-%m-%d") 

        end = request.form.get("filter-end")
        if (end == ""):
            end = None
        else:
            try:
                end = date.fromisoformat(end)
            except:
                end = date.strptime(end, "%Y-%m-%d") 

        # Checks start is before end
        if (start and end): 
            if (start > end):
                flash("Error: Please end date must be after start date")
                return redirect("/")
        

        app.logger.debug("getTrxData called with: start=%s end=%s account=%s category=%s type=%s", start, end, account, category, trxType)
        
        trasactions = getTrxData(start, end, account, category, trxType)

        return render_template("manage_transactions.html", accounts=accounts, categories=categories, transactions=trasactions, types=TYPES)


# Register user
@app.route("/register", methods=["GET", "POST"])
def register():
    if (request.method == "POST"):
        session.clear()
        # Connect to DB
        con = conDbDict()
        cur = con.cursor()

        # Get username
        username = request.form.get("reg_user")

        # Check inputs
        if (not username or not request.form.get("reg_pass1") or not request.form.get("reg_pass2")):
            con.close()
            return render_template("error.html", message="please enter valid username and password")
        if (request.form.get("reg_pass1") != request.form.get("reg_pass2")):
            con.close()
            return render_template("error.html", message="password does not match")
        
        # Check for unique name
        curr_users = cur.execute("SELECT username FROM users").fetchall()
        for row in curr_users:
            if (row["username"] == username):
                con.close()
                return render_template("error.html", message="Username already taken")  

        # Insert user to DB
        hash = generate_password_hash(request.form.get("reg_pass1"), method='scrypt', salt_length=16)
        cur.execute("INSERT INTO users (username, hash) VALUES(?, ?)", (username, hash))
        con.commit()

        # Login user
        session["user_id"] = cur.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchall()[0]["id"]        

        #todo: Close DB & redirect to index
        con.close()
        return redirect("/")
        
    else: 
        return render_template("register.html")
