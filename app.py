from hashlib import new
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
import datetime  # maybe add to inventory db
import addcards

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///caruta.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    user = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])  # Search db for users info
    return render_template("index.html",user=user)


# redirect homepage
#@app.route("/index.html")
#def home():
#    return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        user_name = request.form.get("username")
        password = request.form.get("password")

        if not user_name or not password:
            return apology("must provide username/password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

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


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure confirm password was same
        elif not request.form.get("confirmation"):
            return apology("passwords did not match", 400)
    
        # Ensure email was submitted
        elif not request.form.get("email"):
            return apology("must provide password email", 400)
        
        # Ensure same password
        if request.form.get("confirmation") != request.form.get("password"):
            return apology("passwords did not match", 400)

        # vars for creds
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        pass_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        
        if len(db.execute("SELECT * FROM users WHERE username == ?", username)) or len(
            db.execute("SELECT * FROM users WHERE email == ?", email)) > 0: #username already in use
            return apology("username already exist or email in use", 400)
        #("SELECT * FROM users WHERE username == ? AND email = ?", username, email)
        
        db.execute("INSERT INTO users (username, hash, email) VALUES (?, ?, ?)", username, pass_hash, email)
        flash("Register Complete!")
        return render_template("login.html")
    else:
        return render_template("register.html")
    
   
@app.route("/reset", methods=["GET", "POST"])
def reset():
    """Register user"""
    if request.method == "POST":
        email = request.form.get("email")
        old_password = request.form.get("old_pass")
        new_password = request.form.get("new_pass")
        confirm_password = request.form.get("confirm_new_pass")
        
        print(email, old_password, new_password, confirm_password)
        if not email or not old_password or not new_password:  # one of fields not submitted
            return apology("email, old password, or new password NOT submitted", 400)
        
        if confirm_password != new_password:  # new password and confirm are not the same
            return apology("passwords did not match", 400)
        
        user_db = db.execute("SELECT * FROM users WHERE email = ?", email)  # get user info for email used
        if len(user_db) == 0:  # email not in db
            return apology("email NOT in db", 400)
        
        new_pass_hash = generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=8)
        
        if old_password == "password":
            db.execute("UPDATE users SET hash = ? WHERE email = ?", new_pass_hash, email)
            flash("Password changed")
            return render_template("login.html")
        
        if not check_password_hash(user_db[0]["hash"], old_password):  # old password wasnt same in db
            return apology("old password doesnt match", 400)
        try:
            db.execute("UPDATE users SET hash = ? WHERE email = ?", new_pass_hash, email)    
        except:
            return apology("didnt change", 400)
        
        flash("Password changed")
        return render_template("login.html")
    else:
        return render_template("reset.html")

    
@app.route("/drop", methods=["GET"])
@login_required
def drop():
    user = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])  # Search db for users info
    user_credit = user[0]["credits"]
    credits_roll = 100
    
    if user_credit <= credits_roll:
        flash("Not enough credits")
        return redirect("/inventory")
    uptd_credits = user_credit - credits_roll
    db.execute("UPDATE users SET credits = ? WHERE id = ?", uptd_credits, user[0]["id"])
    
    high_card_id = db.execute("SELECT DISTINCT card_id FROM cards;")
    # make list of random card_id numbers
    #card_num_list = addcards.random_list([0,0,0], 12)  # for testing with card images use line below for real db
    card_num_list = addcards.random_list([0,0,0], len(high_card_id) - 1)
    card_id_list = [i for i in range(len(card_num_list))]  # make beater list the same length as card_num_list
    
    for i in range(len(card_num_list)):
        card = db.execute("SELECT * FROM cards WHERE card_id = ? AND status == 'FALSE'",
                          card_num_list[i])  # search for unpicked up cards with card_id
        if len(card) > 0:  # free card in db
            card_id_list[i] = card[0]["id"]
        else: # no free card with card_id in db
            card_name = db.execute("SELECT * FROM cards WHERE card_id == ?", 
                                   card_num_list[i])  # get card name from db
            db.execute("INSERT INTO cards (card_id, image_id, card_name) VALUES (?, ?, ?)",
                       card_num_list[i],card_num_list[i], card_name[0]["card_name"])  # add card with card_id in db
            highest_card_id = db.execute("SELECT * FROM cards ORDER BY id DESC")  # get id number from most recent card
            card_id_list[i] = highest_card_id[0]["id"]
    
    date = datetime.datetime.now()  # get current time and date
    db.execute("INSERT INTO drops (user_id, card1, card2, card3, time) VALUES ( ?, ?, ?, ?, ?) ", 
           user[0]["id"], card_id_list[0], card_id_list[1], card_id_list[2], date)  # add cards from drop to drops db
    
    card_db = db.execute("SELECT * FROM cards;")  # get updated db
    user = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])  # update user info from db
    #print(f"Card num list: {card_num_list}")  # testing card_id number list
    #print(f"Card id list: {card_id_list}")  # testing unique_id number list
    global card_choices
    card_choices = card_id_list
    return render_template("drop.html",user=user, len=len(card_id_list), 
                           card_db=card_db,card_id_list=card_id_list)

 
@app.route("/pickup1", methods=["GET","POST"])
@login_required
def pickup1():
    if request.method == "POST":
        '''
        get card id 
        change card to picked up
        add card to user_id inventory
        '''
        # card_choices[0] is unique id number for card
        drop_db = db.execute("SELECT * FROM drops WHERE user_id = ? ORDER BY time DESC LIMIT 1", 
                             session["user_id"])  # gets info on most recent drops from user
        unique_card_id = drop_db[0]["card1"]  # get card id for card
        user_id = session["user_id"]  # get user id
        db.execute("UPDATE cards SET status = 'TRUE', user_id = ? WHERE id = ?", 
                   user_id, unique_card_id)  # change card status to true (picked up) and set owner
        db.execute("INSERT INTO inventory (user_id, card_id) VALUES (?, ?) ", 
                   user_id, unique_card_id)  # add card to persons inventory
        return redirect("/inventory")
    else:
        return redirect("/")
    
    
@app.route("/pickup2", methods=["GET","POST"])
@login_required
def pickup2():
    if request.method == "POST":
        # card_choices[0] is unique id number for card
        drop_db = db.execute("SELECT * FROM drops WHERE user_id = ? ORDER BY time DESC LIMIT 1", 
                             session["user_id"])  # gets info on most recent drops from user
        unique_card_id = drop_db[0]["card2"]  # get card id for card
        user_id = session["user_id"]  # get user id
        db.execute("UPDATE cards SET status = 'TRUE', user_id = ? WHERE id = ?", 
                   user_id, unique_card_id)  # change card status to true (picked up) and set owner
        db.execute("INSERT INTO inventory (user_id, card_id) VALUES (?, ?) ", 
                   user_id, unique_card_id)  # add card to persons inventory
        return redirect("/inventory")
    else:
        return redirect("/")
    
    
@app.route("/pickup3", methods=["GET","POST"])
@login_required
def pickup3():
    if request.method == "POST":
        # card_choices[0] is unique id number for card
        drop_db = db.execute("SELECT * FROM drops WHERE user_id = ? ORDER BY time DESC LIMIT 1", 
                             session["user_id"])  # gets info on most recent drops from user
        unique_card_id = drop_db[0]["card3"]  # get card id for card
        user_id = session["user_id"]  # get user id
        db.execute("UPDATE cards SET status = 'TRUE', user_id = ? WHERE id = ?", 
                   user_id, unique_card_id)  # change card status to true (picked up) and set owner
        db.execute("INSERT INTO inventory (user_id, card_id) VALUES (?, ?) ", 
                   user_id, unique_card_id)  # add card to persons inventory
        return redirect("/inventory")
    else:
        return redirect("/")
    
    
@app.route("/inventory", methods=["GET"])
@login_required
def inventory():
    user_id = session["user_id"]
    user = db.execute("SELECT * FROM users WHERE id = ?", user_id)  # Search db for users info
    
    columns = 4  # number of columns in table
    cards_recent = []  # empty list to add dicts to of user
    card_years = []
    user_inventory = db.execute("SELECT * FROM inventory WHERE user_id = ?", user_id)  # gets items from user's inventory
    for id in user_inventory:
        card_db = db.execute("SELECT * FROM cards WHERE id = ?", 
                             id["card_id"])  # gets card info for each card id
        cards_recent.append(card_db[0]["card_id"])  # add card info to users list of dicts
    #print(cards_recent)

    
    filters = ["recent", "year", "make", "car_number"]        
    return render_template("inventory.html", user=user, cols = columns, cards_length=len(cards_recent), 
                           cards_recent = cards_recent, filters=filters)

@app.route("/credits", methods=["GET","POST"])
@login_required
def credits():
    user = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])  # Search db for users info
    
    if request.method == "POST":
        promo_codes = ["TEST", "ADD", "ONE TIME", "ALE IS GAY"]
        promo_prizes = [1000, 5000, 100, 1000000]
        
        code = request.form.get("code").upper()
        for i in range(len(promo_codes)):
            if code == promo_codes[i]:
                current_credits = user[0]["credits"]
                credit_to_add = promo_prizes[i]
                uptd_credits = current_credits + credit_to_add
                db.execute("UPDATE users SET credits = ? WHERE id = ?", uptd_credits, user[0]["id"])
                flash("credits added")
                return redirect("/inventory")
        flash("promocode not accepted")
        return render_template("credits.html", user=user)
    else:
        return render_template("credits.html", user=user)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
    
    