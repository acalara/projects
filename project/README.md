# Jomalert
### Video Demo:  [Youtube Link](https://youtu.be/Z4XhRCAiFNI)

### Description:
Jomalert is a price checking web application that references and checks data daily from the website Jomashop.com. If you're unfamiliar, Jomashop.com  is a popular website that sells grey market luxury items such as handbags, sunglasses, most notably, watches.

### Jomalert Functionality:
The user will initially be prompted to log in or alternatively, register, if a first time visitor. ![Registration](/project/screenshots/1.jpg) ![Login](/project/screenshots/2.jpg)
After logging in, the front page will ask for a product link from Jomashop.com as demonstrated here: ![Index](/project/screenshots/3.jpg) ![Product page](/project/screenshots/4.jpg) ![Product paste](/project/screenshots/5.jpg)
User will then input the length of time to perform daily checks and click **Set Alert**.
Once the valid product link has been processed, the current price data, as well as the start and end date for the alerts will be saved into a database table, and the user will receive a confirmation message and an email. ![Confirmation](/project/screenshots/6.jpg) ![Email](/project/screenshots/7.jpg)
Now, once a day until the end date set for each particular product, a Check application (Python script) will be run which will compare the recorded price with the current price. More details on that below.
The second page of the Jomalert application is the History page shown here. ![History](/project/screenshots/8.jpg)
Here, you can look through the price history for each item that you currently have an alert set for. ![Price history](/project/screenshots/9.jpg)
Prices and dates will only be recorded once there is a change in either direction for price. You will also be alerted via email if such a change occurs. Once the alert has reached its end date, the price alert data for that particular item will be deleted from the database and an email will be sent to notify you.
On the History page, you also have the option to **Update Alert** and **Cancel Alert**. **Update Alert** will update the end date for your daily alerts, and **Cancel Alert** will delete your product data from the database. Both actions result in an email notifying you of such.
Here is the pop-up that appears to confirm once you have clicked on **Cancel Alert**. ![Cancel alert](/project/screenshots/10.jpg)

### How Jomalert Works:
#### App.py
This file, written in Python, contains the main components of the application. The tools utilized include:
- Flask - The framework for the application
- CS50 - The helper function to work with SQL data
- Selenium WebDriver - Tool used to extract live product data
- Datetime - A function for calling and formatting time data
- SMTPlib and MIMEText - Tools used in conjunction to be able to send emails using Python and the gmail account jomalertmail@gmail.com
##### Functionality:
- Register new user data. Input an email and a password, along with password confirmation, that will be hashed then stored into a database table.
- Log in existing users. Check input for matches within database then restore user data if applicable.
- Log out existing users.
- Index function will accept valid product link data and duration time and store this data into a database table.
- History function will pull history data from database and show to user. It will also update end dates for alerts and cancel alerts if prompted by the user. The user will be notified of any changes via onscreen confirmation message and an email.

#### Check.py
This file, written in Python, contains the script which is run daily via personal computer. The tools utilized include:
- Flask - The framework for the application
- CS50 - The helper function to work with SQL data
- Selenium WebDriver - Tool used to extract live product data
- Datetime - A function for calling and formatting time data
- SMTPlib and MIMEText - Tools used in conjunction to be able to send emails using Python and the gmail account jomalertmail@gmail.com
- Cron - Tool for running script on personal computer at an automated interval (set to daily).
##### Functionality:
- Pull up alerts to check via database table and iterate through each item.
- Check if the current date is greater than or equal to the end date set. Delete from database if true, and send an email notification.
- Check live product data using Selenium to see if it matches with stored product data in the database. If there is a mismatch, send an email notification and update both the Alerts and History database tables.
- Run once a day.

#### Helpers.py
##### Functionality:
- Apology message on special page if an error occurs.
- Require login to use the app.
- USD formatting function.
- Function to send emails from jomalertmail@gmail.com to user email.

#### Project.db
##### Functionality:
- Store user data using SQL
- 3 tables: alerts, history, users.
- Alerts contains the following: ID, user ID, name (of product), product link, start date (date when alert was set), end date.
- History contains the following: ID, alerts ID, price, date
- Users contains the following: ID, email, hash (encrypted password).

#### Layout.html
The main layout page includes a clickable logo for returning to the homepage and a menu bar for reaching the history, register, login, and logout pages.

#### Index.html
Contains a box for pasting the product link and a dropdown menu with 3 default options for set duration.

#### History.html
Contains a dropdown box showing your current set alerts to choose from. Data is pulled via project.db database. Once an item is selected, price history is shown along with the options to update or cancel the alert. Update function includes a calendar.

#### Register.html
Register by inputting a valid email address and a password along with a confirmation of said password.

#### Login.html
Log in the app by using email and password which will be checked with database table.

#### Apology.html
Page for when errors occur.

#### Styles.css
The primary inspiration for design was dark mode and pink highlights. Buttons are set to glow and change color when hovered.

### Miscellaneous
My thought process regarding the final project started with brainstorming. To my knowledge, there were no price trackers for Jomashop.com, a site where I had recently made a purchase from. Once I had settled on that idea, I had to figure out how to pull live data from their website. I stumbled upon the Selenium WebDriver, a popular tool for scraping data, and struggled for a good while until I could successfully do what my app intended to do.

From there, I outlined the main functions that I wanted my app to have and considered my tools to complete the project. I chose to write in Python and use Flask considering it was the right mix of flexible functionality and familiarity. SQL and SQLite were tools that I used for storing my user data because of my experience taking CS50 and utilizing them.

The main design theme of the website was inspired by K-Pop supergroup Blackpink. Simple yet trendy concept. This was implemented using CSS and a little help from Bootstrap.

There was not much Javascript used, save for 1 line of code to confirm whether the user wanted to cancel their alert. This was intentional because of my relatively heightened familiarity with Python and the perceived difficulty of web scraping content using Javascript.

Cron was a tool that I discovered when researching tools to run automated scripts. It was not the only tool that I found, but it seemed like the easiest and simplest to use.