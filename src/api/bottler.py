from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/deliver/{order_id}")
# posts delivery of potions, order_id = value of single delivery
def post_deliver_bottles(potions_delivered: list[PotionInventory], order_id: int):
    red_ml = 0
    green_ml = 0
    blue_ml = 0

    # - mL, + potions 
    with db.engine.begin() as connection:
        for potion in potions_delivered:
            red_ml += (potion.quantity * potion.potion_type[0])
            green_ml += (potion.quantity * potion.potion_type[1])
            blue_ml += (potion.quantity * potion.potion_type[2])
            
            connection.execute(sqlalchemy.text(
                    """
                    INSERT INTO potion_ledger (change, potion_sku, description)
                    VALUES (:quantity, 
                            (SELECT sku FROM potions WHERE type = :potion_type), 
                            'new potions bottled')
                    """
                    ), {"potion_type": potion.potion_type,"quantity": potion.quantity})
            
        if red_ml != 0:
            connection.execute(sqlalchemy.text('''INSERT INTO ml_ledger (ml_type, change, description)
                                            VALUES ('red_ml', :change, 'red ml used in bottling')'''), {"change": -1* red_ml})
        if blue_ml != 0:
            connection.execute(sqlalchemy.text('''INSERT INTO ml_ledger (ml_type, change, description)
                                            VALUES ('blue_ml', :change, 'blue ml used in bottling')'''), {"change": -1 * blue_ml})
        if green_ml != 0:
            connection.execute(sqlalchemy.text('''INSERT INTO ml_ledger (ml_type, change, description)
                                            VALUES ('green_ml', :change, 'green ml used in bottling')'''), {"change": -1* green_ml})
            
    print(f"potions delievered: {potions_delivered} order_id: {order_id}")

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    with db.engine.begin() as connection:
        red_ml = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(change), 0) FROM ml_ledger WHERE ml_type = 'red_ml'")).scalar()
        green_ml = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(change), 0) FROM ml_ledger WHERE ml_type = 'green_ml'")).scalar()
        blue_ml = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(change), 0) FROM ml_ledger WHERE ml_type = 'blue_ml'")).scalar()
        potions_catalog = connection.execute(sqlalchemy.text("SELECT type FROM potions"))

        ml_dict = {}
        ml_dict[0] = red_ml
        ml_dict[1] = green_ml
        ml_dict[2] = blue_ml
        ml_dict[3] = 0

        plan = []
        # return [i for i, val in enumerate(arr) if val != 0]

        for potion in potions_catalog:
            make = []
            mls = []
            for i in range(len(potion.type)):
                if potion.type[i] > 0: # doesn't add makes unless it is in the potion
                    make.append(ml_dict[i]//potion.type[i]) 
                    mls.append(i)
                        
            quant = min(make)

            print(ml_dict, make, quant)

            if quant > 0:
                plan.append({
                    "potion_type": potion.type,
                    "quantity": quant,
                })
            
            for ml in mls:
                ml_dict[ml] -= potion.type[ml] * quant

    return plan

'''
200 redml 0 blue 0 green
[50,0,50,0] -> redml//50 = 4, blueml//50 = 0
quant = min 
'''
    
if __name__ == "__main__":
    print(get_bottle_plan())