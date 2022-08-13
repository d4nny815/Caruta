# CS50 Final Project - Caruta Card Game
#### Video Demo:  <URL HERE>
#### Description:
Danny Gutierrez Project

The project is a webpage is based off of Karuta card game on discord. The user uses their credits to roll 3 random car cards and can choose 1 to add to their inventory. The goal is build the best card collection.

Technologies used:

- Python
- Flask
- Jinja2
- sqlite3
- other small libraries or packages

## How the webpage works?

The user registers to make their account. During registration you need to enter these fields:

- Email
- Username
- Password:
- Confirm Pass: it is checked to match

All input boxes allow all alphabet letters and number and only certain special characters.

With the login you can now start rolling for cards. 
Each card has unique id, card id, image id, pickup status, and card name. In the database and a list is made with the card id to pick which cards will drop and then drop free versions (not picked up) of those cards. It change the status of their cards and add that unique card id to the users inventory. The cards with then appear in the user's inventory and the top part will show the most recent card picked up. The credit system accepts codes to give more credits.


### Routing

Each route checks if the user is authenticated. It means if correct username and password were supplied. So they can look at their inventory, add credits, or roll cards.


### Database

Database stores all users, inventory, drops, and cards. The tables.

## Possible improvements

As all applications this one can also be improved. Possible improvements:

- Confirm through an email to fully register account
- Sort inventory (ex. oldest card, year of card)
- Search inventory for certain cards
- Ability to click on card to show stats (ex. that version of card it is 1/100)
- Add multiple edition of cards
- Forgot password and validate through email
- make html nice to look at

#### app.py:
main app file
- handles functions for each route


#### addcards.py:
my made helper file
- Generate random list of nonrecurring numbers (used for card ids)
- unclaim all cards in db
- claim all certain cards (made for testing generating new cards)
- Add new cards
    - checks if the card already exist in db and make new unique id
    - make a new card if its not in db with new card id and card name

#### helpers.py:
cs50 helper file for apology and login required functions



