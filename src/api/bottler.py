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
            red_ml += (potion.quantity * potion.potion_type[0])
            green_ml += (potion.quantity * potion.potion_type[1])
            blue_ml += (potion.quantity * potion.potion_type[1])

            connection.execute(sqlalchemy.text("UPDATE potions SET quantity = quantity + :quant WHERE type = :type"), {"type": potion.potion_type, "quant": potion.quantity})
            
        total_ml = red_ml+ blue_ml + green_ml

        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = num_red_ml - :red_ml"), {"red_ml": red_ml})
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_potions = num_potions + :quant"), {"quant": num_potions})
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = num_green_ml - :green_ml"), {"green_ml": green_ml}) 
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_ml = num_blue_ml - :blue_ml"), {"blue_ml": blue_ml})
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_ml = num_ml - :ml"), {"ml": total_ml})

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
        potions = connection.execute(sqlalchemy.text("SELECT type FROM potions"))

        plan = []

        for potion in potions:
            make_red = red_ml // potion.type[0]
            make_green = green_ml // potion.type[1]
            make_blue = blue_ml // potion.type[2]
            # make dark

            make = min(make_red, make_green, make_blue)
            if make > 1:
                make = make // 2

            plan.append({
                "potion_type": potion.type,
                "quantity": make,
            })
            red_ml -= potion.type[0] * make
            green_ml -= potion.type[1] * make
            blue_ml -= potion.type[1] * make

    return plan

    
if __name__ == "__main__":
    print(get_bottle_plan())