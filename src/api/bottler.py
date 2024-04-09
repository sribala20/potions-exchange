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
    for potion in potions_delivered:
         # - mL, + potions 
        with db.engine.begin() as connection:
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = num_green_ml - 100"))
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_potions = num_green_potions + 1"))
           
    print(f"potions delievered: {potions_delivered} order_id: {order_id}")

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    """
    with db.engine.begin() as connection:
        total_ml = 0
        green_potions = 0
        result = connection.execute(sqlalchemy.text("SELECT num_green_ml from global_inventory"))
        total_ml = result.scalar
        green_potions = total_ml // 100

    # Each bottle has a quantity of what proportion of red, blue, and
    # green potion to add.
    # Expressed in integers from 1 to 100 that must sum up to 100.

    # Initial logic: bottle all barrels into GREEN potions.

    return [
            {
                "potion_type": [0, 100, 0, 0],
                "quantity": green_potions,
            }
        ]

if __name__ == "__main__":
    print(get_bottle_plan())