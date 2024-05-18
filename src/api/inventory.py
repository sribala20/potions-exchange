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

        connection.execute(sqlalchemy.text("""UPDATE global_inventory SET num_potions = :potions"""),
                                    {'potions' : num_potions})
        connection.execute(sqlalchemy.text("""UPDATE global_inventory SET gold = :gold"""),
                                    {'gold' : gold})
        connection.execute(sqlalchemy.text("""UPDATE global_inventory SET num_ml = :num_ml"""),
                                    {'num_ml' : num_ml})

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
        num_potions = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(change), 0) FROM potion_ledger")).scalar()
        num_ml = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(change), 0) FROM ml_ledger")).scalar()
        curr_ml_cap = connection.execute(sqlalchemy.text("SELECT curr_ml_cap FROM global_inventory")).scalar()
        curr_pot_cap = connection.execute(sqlalchemy.text("SELECT curr_pot_cap FROM global_inventory")).scalar()

        pot_cap = 0
        ml_cap = 0
        g = 0.5 * gold # spend only 1/2 on capacity
        
        # check if potions or ml is over 90% current capacity, buys if there is enough gold.
        if g > 1000:
            if num_potions >= 0.9(curr_pot_cap):
                pot_cap += 1
                g -= 1000

        if g > 1000:
            if num_ml >= 0.9(curr_ml_cap):
                ml_cap += 1
            

    return {
        "potion_capacity": pot_cap,
        "ml_capacity": ml_cap
        }

class CapacityPurchase(BaseModel):
    potion_capacity: int
    ml_capacity: int

# Gets called once a day
@router.post("/deliver/{order_id}")
def deliver_capacity_plan(capacity_purchase : CapacityPurchase, order_id: int):
    if capacity_purchase.potion_capacity > 0 and capacity_purchase.ml_capacity > 0:
        payment = (-1000 * capacity_purchase.potion_capacity + -1000 * capacity_purchase.ml_capacity)
        with db.engine.begin() as connection:
            connection.execute(sqlalchemy.text('''INSERT INTO gold_ledger (change, description)
                                           VALUES (:change, 'capacity purchased')'''), {"change": payment})
            connection.execute(sqlalchemy.text("""UPDATE global_inventory SET curr_pot_cap = curr_pot_cap + 1000 """))
            connection.execute(sqlalchemy.text("""UPDATE global_inventory SET curr_ml_cap = curr_ml_cap + 10000"""))
       
    """ 
    Start with 1 capacity for 50 potions and 1 capacity for 10000 ml of potion. Each additional 
    capacity unit costs 1000 gold.
    """
    
    return "OK"
