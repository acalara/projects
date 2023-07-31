from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from cs50 import SQL
import datetime
import os
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from helpers import apology, usd, login_required, send_email
from werkzeug.security import check_password_hash, generate_password_hash

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Initialize database
db = SQL("sqlite:///" + os.getcwd() + "/project.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    # Pull user profile data
    user_id = session["user_id"]
    user = db.execute("SELECT * FROM users WHERE id = ?", user_id)
    user = user[0]
    if request.method == "POST":
        # Initalize headless browser via Selenium
        options = Options()
        options.add_argument('--headless')
        PATH = Service(r"/127158890/project/selenium/chromedriver.exe")
        driver = webdriver.Chrome(service=PATH, options=options)

        # User input Jomashop product page
        link = request.form.get("product")
        # Check if valid page
        driver.get(link)

        # User input email address to be alerted
        email = user["email"]

        # User input duration of product alerts
        # Check for valid input
        if not request.form.get("duration"):
            driver.quit()
            return apology("Must input duration", 400)
        elif not request.form.get("duration").isnumeric():
            driver.quit()
            return apology("enter valid input for duration", 400)
        duration = int(request.form.get("duration"))
        if not duration > 0:
            driver.quit()
            return apology("enter valid input for duration", 400)

        # Search product page for price
        try:
            price_element = WebDriverWait(driver, timeout=3).until(lambda d: d.find_element(By.XPATH, "//div[@class='now-price']/span"))
            price = float(price_element.text.split("$")[1].replace(',',''))
        # Alert if invalid
        except:
            driver.quit()
            return apology("An error occurred while searching for price", 400)

        # Search product page for product name
        try:
            name_element1 = driver.find_element(By.CLASS_NAME, "brand-name")
            name_element2 = driver.find_element(By.CLASS_NAME, "product-name")
            name1 = name_element1.text
            name2 = name_element2.text
            name = name1 + " " + name2
        except:
            driver.quit()
            return apology("A naming error occurred", 400)

        # Check if product + user id already in database
        alerts_id = db.execute("SELECT id FROM alerts WHERE user_id = ? AND product_link = ?", user_id, link)
        if not alerts_id:
            # Insert new price alert product into database
            start_date = datetime.datetime.now()
            end_date = start_date + datetime.timedelta(days=duration)
            db.execute("INSERT INTO alerts (user_id, name, product_link, price, start_date, end_date) VALUES(?, ?, ?, ?, ?, ?)", user_id, name, link, price, start_date, end_date)
            alerts_id = db.execute("SELECT id FROM alerts WHERE user_id = ? AND product_link = ?", user_id, link)
            db.execute("INSERT INTO history (alerts_id, price, date) VALUES(?, ?, ?)", alerts_id[0]["id"], price, start_date)
        else:
            driver.quit()
            flash('Email already receiving alerts for ' + name + '.')
            return render_template("index.html")
        
        # Send intial email
        subject = "Set New Jomalert Price Alert - " + name
        body = "You have set a new price alert for " + name + ".  Currently: " + usd(price) + "."
        sender = "jomalertmail@gmail.com"
        recipients = [email]
        password = "vwqpdhmhyqucxwcv"

        send_email(subject, body, sender, recipients, password)

        # Close Selenium webdriver
        driver.quit()
        flash('Your price alert for ' + name + ' has been set.')
        return render_template("index.html")
    else:
        return render_template("index.html")
    

@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    # List price history for current user for each watch they currently have on alerts table
    # Pull user profile data
    user_id = session["user_id"]
    user = db.execute("SELECT * FROM users WHERE id = ?", user_id)
    user = user[0]
    email = user["email"]

    # Pull name of watch, start date, end date
    # Pull reference data from db
    alerts = db.execute("SELECT * FROM alerts WHERE user_id = ?", user_id)

    if request.method == "POST":
        # Find and show product history
        if request.form.get("product"):
            id = request.form.get("product")
            info = db.execute("SELECT * FROM alerts WHERE id = ?", id)
            history = db.execute("SELECT * FROM history WHERE alerts_id = ?", id)
            now = datetime.datetime.now()
            date_now = now.strftime('%Y-%m-%d %H:%M:%S')
            return render_template("history.html", alerts=alerts, history=history, info=info, date_now=date_now)
        # Cancel an alert
        elif request.form.get("cancel"):
            id = request.form.get("id")
            # Pull name from table using id from HTML
            name = db.execute("SELECT * FROM alerts WHERE id = ?", id)
            name = name[0]["name"]
            # Delete because foreign key connection
            db.execute("DELETE FROM history WHERE alerts_id = ?", id)
            db.execute("DELETE FROM alerts WHERE id = ?", id)
            # Update alerts to be pass through to next page
            alerts = db.execute("SELECT * FROM alerts WHERE user_id = ?", user_id)
            # Send an email notifying of cancellation
            subject = "Cancelled Price Alert - " + name
            body = "You have successfully cancelled the price alert for " + name + "."
            sender = "jomalertmail@gmail.com"
            recipients = [email]
            password = "vwqpdhmhyqucxwcv"

            send_email(subject, body, sender, recipients, password)
            flash('Your alerts for ' + name + ' have been cancelled.')
            return render_template("history.html", alerts=alerts)
        # Update an alert end date
        elif request.form.get("date"):
            id = request.form.get("id")
            # Pull name from table using id from HTML
            name = db.execute("SELECT * FROM alerts WHERE id = ?", id)
            name = name[0]["name"]
            # Format date
            date = request.form.get("date") + " 00:00:01"
            db.execute("UPDATE alerts SET end_date = ? WHERE id = ?", date, id)
            # Send an email notifying of updated
            subject = "Updated Price Alert - " + name
            body = "You have successfully updated the price alert for " + name + ".  The end date is now " + date + "."
            sender = "jomalertmail@gmail.com"
            recipients = [email]
            password = "vwqpdhmhyqucxwcv"

            send_email(subject, body, sender, recipients, password)
            flash('Your alerts end date for ' + name + ' has been updated.')
            return render_template("history.html", alerts=alerts)
        else:
            return render_template("history.html", alerts=alerts)
    else:
        return render_template("history.html", alerts=alerts)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure email was submitted
        if not request.form.get("email"):
            return apology("must provide email", 400)

        # Ensure unique email
        userlist = db.execute("SELECT * FROM users")
        for user in userlist:
            if request.form.get("email") == user["email"]:
                return apology("email already in use", 400)

        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must confirm password", 400)

        # Ensure password and confirmation matches
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("password and confirmation must match", 400)

        # Insert email and hashed password into table
        db.execute("INSERT INTO users (email, hash) VALUES(?, ?)",
                   request.form.get("email"), generate_password_hash(request.form.get("password")))

        # Redirect user to homepage/login
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("email"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE email = ?", request.form.get("email"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")