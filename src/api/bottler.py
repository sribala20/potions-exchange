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
    num_potions = 0
    red_ml = 0
    green_ml = 0
    blue_ml = 0

    # - mL, + potions 
    with db.engine.begin() as connection:
        for potion in potions_delivered:
            num_potions += potion.quantity
            if potion.potion_type == [100,0,0,0]:
                red_ml += (potion.quantity * 100)
            elif potion.potion_type == [0,100,0,0]:
                green_ml += (potion.quantity * 100)
            elif potion.potion_type == [0,0,100,0]:
                blue_ml += (potion.quantity * 100)
            elif potion.potion_type == [50,0,50,0]:
                red_ml += (potion.quantity * 50)
                blue_ml += (potion.quantity * 50)
            else:
                raise Exception("Unidentified potion type.")
            
            connection.execute(sqlalchemy.text("UPDATE potions WHERE type = :type SET quantity = quantity + :quant"), {"type": potion.potion_type, "quant": potion.quantity})
            
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = num_red_ml - :red_ml"), {"red_ml": red_ml})
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_potions = num_potions + :quant"), {"quant": num_potions})
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = num_green_ml - :green_ml"), {"green_ml": green_ml}) 
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_ml = num_blue_ml - :blue_ml"), {"blue_ml": blue_ml})
    
    print(f"potions delievered: {potions_delivered} order_id: {order_id}")

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    with db.engine.begin() as connection:
        red_ml = connection.execute(sqlalchemy.text("SELECT num_red_ml from global_inventory")).scalar()
        green_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml from global_inventory")).scalar()
        blue_ml = connection.execute(sqlalchemy.text("SELECT num_blue_ml from global_inventory")).scalar()

        purple_usage = min(red_ml//2, blue_ml//2)# mix half of red and blue into purple
        purple_potions = purple_usage // 50
        red_ml -= purple_usage
        blue_ml-= purple_usage

        red_potions = red_ml//10
        green_potions = green_ml//10
        blue_potions = blue_ml//10
    
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
            },
            {
                "potion_type": [50, 0, 50, 0],
                "quantity": purple_potions,
            } # is this hardcoding? 
        ]

    
if __name__ == "__main__":
    print(get_bottle_plan())