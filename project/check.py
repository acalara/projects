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
from helpers import apology, usd, send_email

# Daily check in
def main():
    # Initialize database
    db = SQL("sqlite:///" + os.getcwd() + "/project.db")

    # Initalize headless browser via Selenium
    options = Options()
    options.add_argument('--headless')
    PATH = Service(r"/127158890/project/selenium/chromedriver.exe")
    driver = webdriver.Chrome(service=PATH, options=options)

    # Pull reference data from db
    price_list = db.execute("SELECT * FROM alerts")

    # Iterate through list, check date, pull current product prices via selenium, compare
    for i in range(len(price_list)):
        price = price_list[i]["price"]
        name = price_list[i]["name"]
        link = price_list[i]["product_link"]
        id = int(price_list[i]["id"])
        user_id = price_list[i]["user_id"]
        date = datetime.datetime.now()
        date2 = price_list[i]["end_date"]
        end_date = datetime.datetime.strptime(date2, '%Y-%m-%d %H:%M:%S')

        driver.get(link)

        # Check if valid date, update database if necessary, email user
        if date >= end_date:
            # Grab user email
            email = db.execute("SELECT * FROM users WHERE id = ?", user_id)
            email = email[0]["email"]
            # Delete because foreign key connection
            db.execute("DELETE FROM history WHERE alerts_id = ?", id)
            # Delete row from alerts table 
            db.execute("DELETE FROM alerts WHERE id = ?", id)

            # Send alert email
            subject = "Jomalert Price Alert Has Ended for " + name
            body = "Your price alert for " + name + " has ended."
            sender = "jomalertmail@gmail.com"
            recipients = [email]
            password = "vwqpdhmhyqucxwcv"

            send_email(subject, body, sender, recipients, password)
            # Continue iteration through alerts table
            continue

        # Search product page for price
        try:
            price_element = WebDriverWait(driver, timeout=3).until(lambda d: d.find_element(By.XPATH, "//div[@class='now-price']/span"))
            curr_price = float(price_element.text.split("$")[1].replace(',',''))

        # Alert if invalid
        except:
            return apology("An error occurred while searching for price", 400)
        
        # Compare prices, alert if necessary
        if price != curr_price:
            # Grab user email
            email = db.execute("SELECT * FROM users WHERE id = ?", user_id)
            email = email[0]["email"]

            # Send alert email
            subject = "Jomalert Price Alert - " + name
            body = "You have a new price alert for " + name + ".  Currently: " + usd(curr_price) + ".  Was: " + usd(price)
            sender = "jomalertmail@gmail.com"
            recipients = [email]
            password = "vwqpdhmhyqucxwcv"

            send_email(subject, body, sender, recipients, password)

            # Update database tables
            db.execute("UPDATE alerts SET price = ? WHERE id = ?", curr_price, id)
            db.execute("INSERT INTO history (alerts_id, price, date) VALUES(?, ?, ?)", id, curr_price, date)

    # Close Selenium webdriver
    driver.quit()


if __name__ == '__main__':
    main()