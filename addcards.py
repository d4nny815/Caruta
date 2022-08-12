from email.policy import default
import sys
import random
import math
from cs50 import SQL

db = SQL("sqlite:///caruta.db")


'''
#TODO
#add comments to funcs
'''


def main():
    if len(sys.argv) == 3:
        # python3 addcards.py unclaim {password}
        unclaim_all()
        claim_random_cards(sys.argv[2])
        
    # python3 addcards.py year make model
    elif len(sys.argv) != 4:
        print("not enough args")
        return
    
    year = sys.argv[1].upper()
    make = sys.argv[2].upper()
    model = sys.argv[3].upper()
    name = year + ' ' + make + ' ' +  model
    card_db = db.execute("SELECT * FROM cards WHERE card_name == ? ", name)
    
    if len(card_db) > 0:  # card already in db
        card_id = card_db[0]["card_id"]
        image_id = card_db[0]["image_id"]
        db.execute("INSERT INTO cards (card_id, image_id, card_name) VALUES (?, ?, ?) ", 
                   card_id, image_id, name)
        for i in range(len(card_db)):
            set_card_name = card_db[i]["card_name"]
            set_card_id = card_db[i]["card_id"]
            print(f" card name: {set_card_name} card id: {set_card_id} ")
        print("added new card to db")
        return
    
    
    else:  # card new to db
        card_ids = db.execute("SELECT card_id FROM cards ORDER BY card_id DESC")
        highest_card_id = card_ids[0]["card_id"] + 1
        id_count = db.execute("SELECT id FROM cards ORDER BY id DESC")
        id = id_count[0]["id"] + 1
        db.execute("INSERT INTO cards (id, card_id, image_id, status, card_name) VALUES (?,?, ?, 'FALSE', ?) ", 
                   id, highest_card_id, highest_card_id, name)
        print(f" card name: {name} card id: {highest_card_id} ")
        print("Added new card to db that was NOT in db")
        return 1
       
    
def random_list(list, highcard):
    length = len(list)
    randomlist = random.sample(range(1,highcard),length)
    return randomlist


def claim_random_cards(card_id):
    if sys.argv[1] == 'claim' and card_id.isdigit():
        db.execute("UPDATE cards SET status = 'TRUE' WHERE card_id = ?", card_id)
        print("claimed all")
        return 2
    else:
        print("couldnt claim card_number")
        return 1
        

def unclaim_all():
    password = "dog"
    if sys.argv[1] == 'unclaim' and sys.argv[2] == password:
        db.execute("UPDATE cards SET status = 'FALSE', user_id = NULL")
        print("unclaimed all")
        return 2
    else:
        print("not correct unclaim format")
        return 1
    
    
def print_table():
    user_inventory = db.execute("SELECT * FROM inventory WHERE user_id = 1")  # gets users inventory
    items = len(user_inventory)  # gets how many items in inventory
    columns = 4  # random number of columns wanted in table
    rows = math.ceil(items / columns)  # number of rows need to fit items 
    default_col = columns  # var for columns that wont change
    i = 0  # counter var
    
    for row in range(rows):  # makes the number of rows
        for col in range(columns):  # makes number of columns to print
            card_db = db.execute("SELECT * FROM cards WHERE id = ?", 
                                 user_inventory[i]["card_id"])  # gets card info from db going through users inventory
            print("[" ,card_db[0]["card_name"], "]" , end="")  # print the unique id of card
            i += 1  # moves counter over to next item in inventory
        columns =  items - columns  # calc to see how many items left to display
        if columns >= default_col:  # check if items over number of columns wanted 
            items = columns  # sets items leftover
            columns = default_col # sets column back to columns wanted for next row
        print()  # end row
    return

    


if __name__ == '__main__':
    main()
        
        
        
        
        
