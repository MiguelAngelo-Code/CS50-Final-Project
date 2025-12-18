# CS50 Final Project: Personal Finance Tracker

#### Video Demo:  <URL HERE>


## Table of Contents
- [Description](#-description)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Usage](#usage)
- [Design Decisions](#designee-decisions)
- [Limitations](#Limitations--Areas-of-Improvment)


## Description
Having recently relocated to Biel, Switzerland, one off the major adjustments for my family has been managing personal finances.  A new language, different currency and vastly different price’s across everyday essentials, transport, etc.. keeping on top of our monthly spend has been increasingly challenging. 

Hence the reason for the development of a simple personal finance tracker that incorporates a dashboard, providing users with an easy-to-use tool for quickly visualising spending. 


## Features
    -	User authentication & log-in
    -	Create, edit and delete, transactions
        o	Income and expenses  can be categories and assigned to a specific finance account, i.e. “Primary”, “Savings” etc…
    -	Create, edit and delete categories
    -	Create, edit and delete finance accounts
    -	View transaction history and filter by 
        o	Date
        o	Account
        o	Category 
        o	Type
    -	Visualise transaction data
        o	Income vs Expense
        o	Expense Over Time
        o	Spend by Category 


## Tech Stack
    -	**Python** - Core application logic and data processing on the back-end.
    -	**Flask** Lightweight web framework used to handle routing, sessions, and server-side rendering.
    -	**HTML & Jinja2** — Used for rendering dynamic templates and displaying transaction data.
    -	**CSS** — Custom dark theme for consistent UI styling.
    -	**JavaScript** — Handles small UI interactions such as toggling edit states.
    -	**SQLite** — Relational database used to store users, accounts, and transactions.
    -	**matplotlib** — Generates static charts for income and expense visualisation.


## Usage
### Authentication
Each user only has access their own accounts and transactions, and must log-in or register before being able to access the application.
    -	Inputs for username and password are checked at registration/log-in on the front-end HTML and backend python code.
        o	If an input is missing the user will be prompted or shown an error message.
    -	At registration, the user selects a password that will be hashed before being stored in the database for security
    -	At registration, the username is check for uniqueness in the backend python app.py, as well as the SQLite database.
            `# Check for unique name
                    curr_users = cur.execute("SELECT username FROM users").fetchall()
                    for row in curr_users:
                        if (row["username"] == username):
                            con.close()
                            return render_template("error.html", message="Username already taken")`

            `CREATE UNIQUE INDEX ux_users_username_nocase
                ON users(username COLLATE NOCASE`

### Managing Personal Accounts
Users can create one or more accounts within their profile to represent different sources or pools of money such as, bank accounts, cash balance or savings pots. 

Each transaction is always associated with an account, however users do have the ability to summarise data across all accounts in their dashboards. 

Additionally, accounts also track balance which can be viewed on the dashboard. 

### Managing Categories
Users are able to create one or more custom categories to represent different sources of income or expenditure. 

Each transaction is always associated with a user created category.

### Adding Transactions
Users can add income or expense transactions by specifying:
    - Amount
    - Date
    - Category
    - Account
    - Transaction type (income or expense)

All transactions are stored in the SQL database and displayed in a table view via jina2 loops on the front end.

### Editing and Deleting transactions
Existing transactions can be edited directly from the transaction table in the “Manage Transactions” page. 

Each row supports a view and edit state, allowing users to update transaction details without navigating to a separate page.

### Filtering Data
In the “Manage Transaction” page, users can filter history by: 
    -	Date Range
    -	Category
    -	Account
    -	Type. 

In the dashboard page, users can filter history by:
    -	Date Range
    -	Account

Filters apply to both the transaction history table and generated charts. 

### Data visualisation
The application generates charts that visualise income and expenses over time, spend verses income, and spend by category.
  
Charts are generated server-side based on the currently selected filters and displayed as static images.


## Designee Decisions
    1)	Storing account balance: account balances are stored in the accounts table of the database and updated by triggers
        •	**Why** - A feature that prompted me to redesign the database, as I was calculating balance on the backed by summing all transactions on a user account every time a request was made. 
        •	**Trade-off** - faster, simpler and more efficient, however if transactions are modified without firing triggers, balance can become incorrect.


    2)	Server Generated Charts: Charts are generated on the back-end using matplotlib and displayed as static images to keep frontend complexity low.
        •	Why: I chose to use matplotlib because it is well documented, wildly used and introduces low complexity compared to interactive chart libraries. 
        •	Trade-off: Although sufficient for the scope of this application and reducing complexity, charts are static and must be regenerated every time filters are changed. 

    3)	Monetary values stored as integer cents
        •	Why: Another feature that prompted a redesign of the database as I was having issues with floating point errors

    4)	Flexible filtering: A feature that went through many iteration, I eventually settled on a helper function that builds where clause for database queries to generate charts and pull transaction history
        •	Why: initially starting with match case statements within the main app.py file, I quickly ran into problems with combinatorial explosion of cases. Logic became repetitive over multiple functions that required different filters, adding complexity and making it difficult to maintain, expand and debug the feature.
        •	Limitation: The function greatly simplified the app and was re-usable within other functions, such as getBar(), getPie(), getLine() and more. However, the current implementation doesn’t allow for users to select multiple accounts and or categories. This is an area of improvement for future iterations. 


            `def buildWhereClauseTrx(start = None, end = None, accId = None, cat = None, trxType = None):`


## Limitations & Areas of Improvment

    1)	Limited validation and error feedback: Some input validation and error handling could be expanded for a production environment.
    2)	Hardcoded Secrets: The app uses a hardcoded secret key ("some-secret-key"), which is insecure for production.
    3)	Static Charts: Charts are saved to the filesystem, which can accumulate files and isn't scalable for multiple users or deployments.
    4)	No Multi-Currency or Advanced Features: Assumes single currency; no support for transfers between accounts, goals, or financial projections.