from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import math
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/audit")
def get_inventory():
    """ """
    with db.engine.begin() as connection:
        red_potions = connection.execute(sqlalchemy.text("SELECT num_red_potions from global_inventory")).scalar()
        green_potions = connection.execute(sqlalchemy.text("SELECT num_green_potions from global_inventory")).scalar()
        blue_potions = connection.execute(sqlalchemy.text("SELECT num_blue_potions from global_inventory")).scalar()
        red_ml = connection.execute(sqlalchemy.text("SELECT num_red_ml from global_inventory")).scalar()
        green_ml = connection.execute(sqlalchemy.text("SELECT num_green_ml from global_inventory")).scalar()
        blue_ml = connection.execute(sqlalchemy.text("SELECT num_blue_ml from global_inventory")).scalar()
        gold = connection.execute(sqlalchemy.text("SELECT gold from global_inventory")).scalar()
        
        potion_count = red_potions + green_potions + blue_potions
        ml_count = red_ml + green_ml + blue_ml
    
    return {"number_of_potions": potion_count, "ml_in_barrels": ml_count, "gold": gold}

# Gets called once a day
@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

    return {
        "potion_capacity": 0,
        "ml_capacity": 0
        }

class CapacityPurchase(BaseModel):
    potion_capacity: int
    ml_capacity: int

# Gets called once a day
@router.post("/deliver/{order_id}")
def deliver_capacity_plan(capacity_purchase : CapacityPurchase, order_id: int):
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """

    return "OK"
