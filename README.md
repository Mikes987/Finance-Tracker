# Personal Finance Tracker
(*Very early alpha*)

## Project Description
I am creating a personal finance tracker in the python flask framework. The finance tracker is mostly inspired by [Personal Budget Tracker](https://www.youtube.com/watch?v=eKyAOjH3Crk) on Youtube.

### Motivation
I recreated the *Personal Budget Tracker* from the YT videos according to the creator's instructions and with time added some functionality to allow me to have some statistics based on my income and spending.
Furthermore, I found some "bugs" based on calculations and added protected cells and other functionalities to give me the feeling of a complete user product.

However, I came across some issues that motivated me to check for myself if I am able to create similar logics and UIs within a web frame work:
- I would like to implement some more stats based on expenses e.g. nutrition or specific shops which becomes a bit complicated within the original Excel.
- I added currency formatting and a settings option to choose any currency and be integrated along the entire file and sheets.
  - But what If I maintain accounts in different countries with different currencies?
  - In the budget tracker I have this issue solved by using different ones with different currencies.
  - I would like to have all data in one "sheet" though and if different currencies are used, I'd like to have them shown in one chart by calculating with exchange rates.
-   Despite using this project as a practical learning project for python frameworks, I'd like to use my own finance tracker without being too dependent on one particular heavy software such as Excel.
-   One (rather negligible) aspect is language. What if I want to change the language on the UI simply by choosing that option?


## Current stage (31.03.2025)
- This is a very early stage of the application in which I am creating and implementing the core functionalities such as User, dabase tables and data.
- I am currently not focusing on any styles or visuals.
- Currently all functionality within the broswer, no REST APIs.

#### What currently works from a User point of view
- **User** creation, login and restore password.
- Creating your own **Categories** for the main types *Income*, *Expenses*, and *Savings*
  - **Sidenote**: I am also thinking of adding a main type *Debt* as its "logic" is not fully supported on the Excel *Budget Tracker* and good to have in addition from my point of view.
- Inserting data of income, expenses and savings into the **Tracking** page and have it shown in a table on the same page.

#### To consider (from a user point of view)
- Currently, there are no "delete" options included, I am implementing those functionalities piece by piece.
  - You either delete directly in data base or create a new user.
- For currency exchange rate data, I connect to a specific URL but it's not fully implemented as a job yet.
  - The function itself is created, the job logic of when to run isn't.
- As I focus on core functionalities at the moment, I don't fully code with regards to coding standards, i.e. I didn't run any static code analysis on my code. Again, it will be added piece by piece.


#### Components used
- **Flask** webframe work with extensions such as flask-login, flask-wtf
- **Database**: Currently only using SQLite3. To handle database access and maintenance, I'm using SQLAlchemy and Alembic
- **Currency Exchange Rates**: The application connects to [The Exchange Rate API](https://www.exchangerate-api.com/) and takes the Exchange rates from the USD as a simple reference.
  - The simple API doesn't require any API key and data refreshes every 24 hours which is enough during development.
  - Data grabbing currently saved in an external file, inserting functions implemented.


 ## Install and Run
 - clone or download into specific directory on your computer.
 - (Not required but recommended:) create virtual environment in that directory (```python 3 -m venv .venv```)
 - Run ```pip install -r requirements.txt```
 - Make sure, all files of the project are in the directory, including the hidden ones like .flaskenv
   - By running ```flask run```, the application checks content in .flaskenv which points to finance_tracker.py which starts the application.
 - Run the following commands to initialize the database in SQLite. It will be stored in the parent folder.
   - ```flask db init```
   - ```flask db migrate -m "Initiate Tables"```
   - ```flask db upgrade```
 - To set up the initial main types and set of currencies, run the to *initiate....py* files in the directory **initiation_files**
   - ```python3 initiate_maintypes.py```
   - ```python3 initiate_currencies_and_exchanges.py```
 - Run ```flask run```

- Create User and login
- Go to *Settings* and create *View*
  - In *View*, you set the currency for your categories.
- When done, you will see a table with the headers *Income*, *Expenses* and *Savings* and be allowed to create your own views.
- When done, you can navigate to *Tracking* and create your income and expense data.
  - **Note**: There are currently no calculations done, your data is simply displayed in a table.
  - The forms for date and currency currently don't follow any logics to ensure these are indeed dates and numbers. Will be implemented, I was recently dealing with an issue with regards to dynamic select fields and had to solve that first (*Income* main type only allows its categories as the other main types do).


## Special Thanks to
- [The Office Lab](https://www.youtube.com/@theofficelab) for their tutorials.
- [Miguel Grinberg](https://github.com/miguelgrinberg) for his [tutorials](https://blog.miguelgrinberg.com/) on an entire flask project and single topics on how to address issues when buiding a flask project.
