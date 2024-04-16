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
    num_red = 0
    num_green = 0
    num_blue = 0
    for potion in potions_delivered:
        if potion.potion_type == [100,0,0,0]:
            num_red += potion.quantity
        elif potion.potion_type == [0,100,0,0]:
            num_green += potion.quantity
        else:
            num_blue += potion.quantity

        print(potion)
    # - mL, + potions 
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = num_red_ml - :red_ml"), {"red_ml": num_red * 100})
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_potions = num_red_potions + :num_red"), {"num_red": num_red})
        
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = num_green_ml - :green_ml"), {"green_ml": num_green * 100})
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_potions = num_green_potions + :num_green"), {"num_green": num_green})
        
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_ml = num_blue_ml - :blue_ml"), {"blue_ml": num_blue * 100})
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_potions = num_blue_potions + :num_blue"), {"num_blue": num_blue})
        
    print(f"potions delievered: {potions_delivered} order_id: {order_id}")

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    with db.engine.begin() as connection:
        red_potions = connection.execute(sqlalchemy.text("SELECT num_red_ml from global_inventory")).scalar() // 100
        green_potions = connection.execute(sqlalchemy.text("SELECT num_green_ml from global_inventory")).scalar() // 100
        blue_potions = connection.execute(sqlalchemy.text("SELECT num_blue_ml from global_inventory")).scalar() // 100


    if red_potions == 0 and green_potions == 0 and blue_potions == 0:
        return []
    
    return [
            {
                "potion_type": [100, 0, 0, 0],
                "quantity": red_potions,
            }, 
            {
                "potion_type": [0, 100, 0, 0],
                "quantity": green_potions,
            },
            {
                "potion_type": [0, 0, 100, 0],
                "quantity": blue_potions,
            }
        ]


if __name__ == "__main__":
    print(get_bottle_plan())