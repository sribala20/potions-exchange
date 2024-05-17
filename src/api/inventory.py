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
        num_potions = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(change), 0) FROM potion_ledger")).scalar()
        num_ml = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(change), 0) FROM ml_ledger")).scalar()
        gold = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(change), 0) FROM gold_ledger")).scalar()

    print(f"potions: {num_potions} ml: {num_ml} gold: {gold}")
    return {"number_of_potions": num_potions, "ml_in_barrels": num_ml, "gold": gold}

# Gets called once a day
@router.post("/plan")
def get_capacity_plan():
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """
    with db.engine.begin() as connection:
        gold = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(change), 0) FROM gold_ledger")).scalar()
    if gold >= 1000:
        cap = 1


    return {
        "potion_capacity": cap,
        "ml_capacity": cap
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
