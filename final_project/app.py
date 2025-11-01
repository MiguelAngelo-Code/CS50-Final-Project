import io
import calendar
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from flask import Flask, flash, redirect, render_template, Response, request, session
from flask_session import Session
from helpers import getUser, conDbDict, getLine
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
TYPES = ["Expense", "Income"]
CATEGORIES = ["Food", "Insurance", "Salary"] #Todo: add category broken as it adds to consts which reset at login... must insert into db!!

#App routes

# Pages
@app.route("/", methods=["GET", "POST"])
def index():
    # Checks user is loged in
    if ("user_id" not in session):
        return redirect("/login")
    
    # Open DB connection
    con = sqlite3.connect("final.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    # Get user ID
    user = cur.execute("SELECT id, username FROM users WHERE id = ?", (session["user_id"],)).fetchone()

    # Get request
    if (request.method == "GET"):
       
       # Fetch user transaction
       transactions = cur.execute("SELECT * FROM transactions where user_id = ? ORDER BY date", (user["id"],)).fetchall()

       # Calculate Cash Flow
       totExpense = 0.00
       totIncome = 0.00

       for row in transactions:
            # row["type"] = Expense
            if (row["type"] == TYPES[0]):
               totExpense += row["amount"]
            # row["type"] = Income
            elif (row["type"]== TYPES[1]):
               totIncome += row["amount"]
               
       # Render index
       con.close()
       return render_template("index.html", user=user, types=TYPES, categories=CATEGORIES, transactions=transactions, totExpense=totExpense, totIncome=totIncome)
    
    # POST Request
    else:
        #Todo: add feture to click through transaction get ID and see iteams in transaction. will req. new database and input forms
        
        # Get user input
        exType = request.form.get("type")
        category = request.form.get("category")
        amount = request.form.get("amount")
        date = request.form.get("date")

        #Todo: validate all inputs

        # Validates types as this will be used to calculate cash flow
        if (exType not in TYPES):
            return render_template("error.html", message="invalid type submission")

        #insert transaction into database
        cur.execute("INSERT INTO transactions (type, category, amount, date, user_id) values (?, ?, ?, ?, ?)", (exType, category, amount, date, user["id"]))
        con.commit()

        con.close()
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
        con = sqlite3.connect("final.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        # Get user id & hash using lowercase username
        user = cur.execute("SELECT id, hash FROM users WHERE username = ?", (username.lower(),)).fetchall()

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
        con = sqlite3.connect("final.db")
        con.row_factory = sqlite3.Row 
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
        cur.execute("INSERT INTO users (username, hash) VALUES(?, ?)", (username.lower(), hash))
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

        # Line Graph
        try:
            getLine(start, end)
        except:
            return render_template("error.html", message="Error with line graph")
        
        # Todo: bar graph, expense vs income
        # Todo: pie chart spend by category

        return render_template("dashboard.html", chart="static/my_line-expsnses.png")
    
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
        # Todo: pie chart spend by category
        
        return render_template("dashboard.html", chart="static/my_line-expsnses.png")
        

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