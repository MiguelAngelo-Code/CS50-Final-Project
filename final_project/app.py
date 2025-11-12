import io
import calendar
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from decimal import Decimal, ROUND_HALF_UP
from flask import Flask, flash, redirect, render_template, Response, request, session
from flask_session import Session
from helpers import conDbDict, getBar, getLine, getPie, getTrans, getUser
import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

# Configure application
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

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

# Consts
TYPES = ["expense", "income"]
CATEGORIES = ["Food", "Insurance", "Salary"] #Todo: add category broken as it adds to consts which reset at login... must insert into db!!

#App routes

# Pages
@app.route("/", methods=["GET", "POST"])
def index():
    # Checks user is loged in
    if ("user_id" not in session):
        return redirect("/login")
    
    # Open DB connection
    con = conDbDict()
    cur = con.cursor()

    # Get user ID
    user = getUser()

    # Get request
    if (request.method == "GET"):
       
       # Fetch user transaction
       transactions = getTrans()

       # Get user Accounts
       accounts = cur.execute("SELECT account_name, balance_cents, id FROM accounts WHERE user_id = ?", (user["id"],)).fetchall()
               
       # Render index
       con.close()
       return render_template("index.html", accounts=accounts, user=user, types=TYPES, categories=CATEGORIES, transactions=transactions)

    
@app.route("/add_transaction", methods=["GET", "POST"])
def add_transaction():
    if ("user_id" not in session):
        return redirect("/login")
    
    if (request.method == "POST"):
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
        cur.execute("INSERT INTO transactions (account_id, amount_cents, category, created_by_user_id, trans_date, trans_type) values (?, ?, ?, ?, ?, ?)", (account, amount_cents, category, user["id"], date, trans_type))
        con.commit()

        con.close()

        return redirect("/")
    
    else: 
        return redirect("/")


@app.route("/dashboard")
def dashboard():
    if ("user_id" not in session):
        return redirect("login.html")
    
    return redirect("/get_charts")

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
        session["user_id"] = cur.execute("SELECT id FROM users WHERE username = ?", (username.lower(),)).fetchall()[0]["id"]        

        #todo: Close DB & redirect to index
        con.close()
        return redirect("/")
        
    else: 
        return render_template("register.html")

# Functions 
@app.route("/logout")
def logout():

    # Logout user
    session.clear()

    #redirect to index
    return redirect("/")

@app.route("/get_charts", methods=["GET", "POST"])
def get_charts():

    # Generates defualt graphes based on current month
    if (request.method == "GET"):

        # Set start and end dates as first and last day of current month
        current_date = date.today()
        start = current_date + relativedelta(day=1)
        end = current_date + relativedelta(day=31)

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

        return render_template("dashboard.html", chart="static/my_line-expsnses.png", bar="static/my_bar_expesne_vs_income.png", pie="static/my_pie_expenses.png")
    
    # Generates Graphes based on user input
    else:

        # Set user date selction
        start = request.form.get("start")
        end = request.form.get("end")

        # Line Graph
        try:
            getLine(start, end)
        except:
            return render_template("error.html", message="Error with line graph")
        
        # Todo: bar graph, expense vs income
        try:
            getBar(start, end)
        except:
            return render_template("error.html", message="Error with bar graph")
        # Todo: pie chart spend by category
        try:
            getPie(start, end)
        except:
            return render_template("error.html", message="Error with pie graph")

        return render_template("dashboard.html", chart="static/my_line-expsnses.png", bar="static/my_bar_expesne_vs_income.png", pie="static/my_pie_expenses.png")
    
@app.route("/add_cat", methods=["GET", "POST"]) #Todo: add category broken as it adds to consts which reset at login... must insert into db!!
def add_cat():
    if (request.method == "POST"):
        new_cat = request.form.get("new_cat")

        if (new_cat in CATEGORIES):
            return render_template("error.html", message="already in categories")
        else: 
            CATEGORIES.append(new_cat)
            return redirect("/")

    else:
        return render_template("error.html", message="get request to /add_cat")