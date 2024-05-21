from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db    
import itertools 

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    red_ml = 0
    blue_ml = 0
    green_ml = 0
    price = 0

    for barrel in barrels_delivered:
        price += (barrel.price * barrel.quantity)
        if barrel.potion_type == [1,0,0,0]:
            red_ml += (barrel.ml_per_barrel * barrel.quantity)
        elif barrel.potion_type == [0,1,0,0]:
            green_ml += (barrel.ml_per_barrel * barrel.quantity)
        elif barrel.potion_type == [0,0,1,0]:
            blue_ml += (barrel.ml_per_barrel * barrel.quantity)
        else:
            raise Exception("invalid potion type.")
        
    # + mL, - gold
    with db.engine.begin() as connection:
        # try: insert into processed(job_id, type), values order_id and barrels | except: integrityerror
        
        if red_ml != 0:
            connection.execute(sqlalchemy.text('''INSERT INTO ml_ledger (ml_type, change, description)
                                            VALUES ('red_ml', :change, 'red ml added from barrel purchase')'''), {"change": red_ml})

        if blue_ml != 0:
            connection.execute(sqlalchemy.text('''INSERT INTO ml_ledger (ml_type, change, description)
                                            VALUES ('blue_ml', :change, 'blue ml added from barrel purchase')'''), {"change": blue_ml})
        if green_ml != 0:
            connection.execute(sqlalchemy.text('''INSERT INTO ml_ledger (ml_type, change, description)
                                            VALUES ('green_ml', :change, 'green ml added from barrel purchase')'''), {"change": green_ml})

        if price != 0:
            connection.execute(sqlalchemy.text('''INSERT INTO gold_ledger (change, description)
                                            VALUES (:change, 'barrel purchases')'''), {"change": -1 * price})
            
    print(f"gold_paid: {price}, order_id: {order_id}") 
    return "OK"
    
# Gets called once a day
# catalog of av. barrels -> which barrels to purchase and how many
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    print(wholesale_catalog)

    with db.engine.begin() as connection:
        # spend 100% gold on barrels at start
        gold = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(change), 0) FROM gold_ledger")).scalar()
        #gold = connection.execute(sqlalchemy.text("SELECT SUM(change) FROM gold_ledger")).scalar()
     
        gold = gold * .1
        ordered_barrels = barrel_sizes(wholesale_catalog, gold)

    order_plan = []
    for barrel in ordered_barrels:
        if gold < barrel.price:
            break
        order_plan.append({"sku": barrel.sku, "quantity": 1}) #start just buying 1 each
        gold -= barrel.price 
            
        
    print ("barrels:", order_plan)
    print("gold", gold)
    return order_plan
    

# def best_barrels(barrel_lst: list[Barrel]):
#     sorted(barrel_lst, key=lambda barrel: barrel.ml_per_barrel / barrel.price, reverse=True)

# organizes barrels from smallest to largest, allows to iterate and buy smalls of each color first. 
def barrel_sizes(wholesale_catalog: list[Barrel], gold):
    mini_barrels = []
    small_barrels = []
    med_barrels = []
    large_barrels = []

    for barrel in wholesale_catalog:
        if 'MINI' in barrel.sku:
            if gold >= 100:
                continue
            else:
                mini_barrels.append(barrel) 
        elif 'SMALL' in barrel.sku:
            if gold >= 500:
                continue
            else:
                small_barrels.append(barrel) 
        elif 'MEDIUM' in barrel.sku:
            med_barrels.append(barrel) 
        elif 'LARGE' in barrel.sku:
            large_barrels.append(barrel) 
        else:
            raise Exception("Random size.")

    ordered_barrels = med_barrels + large_barrels
    print(ordered_barrels)
    return ordered_barrels   