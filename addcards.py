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
        if unclaim_all() == 2:
            print("stopped at UNCLAIM")
            return
        elif claim_random_cards(sys.argv[2]) == 2:
            print("stopped at CLAIM")
            return
        else:
            print("didnt pass others")
            return 1
        
    # python3 addcards.py year make model
    elif len(sys.argv) == 4:
        add_cards()
        return
    
    else:
        print("Not correct number of args")
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
        db.execute("DELETE FROM inventory")
        db.execute("DELETE FROM drops")
        print("unclaimed all")
        return 2
    else:
        print("not correct unclaim format")
        return 1
       
def add_cards():
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
    

if __name__ == '__main__':
    main()
        
        
        
        
        
