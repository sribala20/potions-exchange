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
        red_ml = connection.execute(sqlalchemy.text("SELECT SUM(change) FROM ml_ledger WHERE ml_type = 'red_ml'")).scalar()
        green_ml = connection.execute(sqlalchemy.text("SELECT SUM(change) FROM ml_ledger WHERE ml_type = 'green_ml'")).scalar()
        blue_ml = connection.execute(sqlalchemy.text("SELECT SUM(change) FROM ml_ledger WHERE ml_type = 'blue_ml'")).scalar()
        potions_catalog = connection.execute(sqlalchemy.text("SELECT type FROM potions"))

        plan = []

        for potion in potions_catalog:
            try:
                make_red = red_ml // potion.type[0]
            except ZeroDivisionError:
                make_red = 0
                print("Cannot divide by zero for make_red.")
                
            try:
                make_green = green_ml // potion.type[1]
            except ZeroDivisionError:
                make_green = 0
                print("Cannot divide by zero for make_green.")
                
            try:
                make_blue = blue_ml // potion.type[2]
            except ZeroDivisionError:
                make_blue = 0
                print("Cannot divide by zero for make_blue.")

            # make dark
            print(make_red, make_green, make_blue)

            make = max(make_red, make_green, make_blue)
            # if make > 1:
            #     make = make // 2

            if make > 0:
                plan.append({
                    "potion_type": potion.type,
                    "quantity": make,
                })

            red_ml -= potion.type[0] * make
            green_ml -= potion.type[1] * make
            blue_ml -= potion.type[2] * make

    return plan

    
if __name__ == "__main__":
    print(get_bottle_plan())