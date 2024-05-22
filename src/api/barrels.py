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
    dark_ml = 0
    price = 0

    for barrel in barrels_delivered:
        price += (barrel.price * barrel.quantity)
        if barrel.potion_type == [1,0,0,0]:
            red_ml += (barrel.ml_per_barrel * barrel.quantity)
        elif barrel.potion_type == [0,1,0,0]:
            green_ml += (barrel.ml_per_barrel * barrel.quantity)
        elif barrel.potion_type == [0,0,1,0]:
            blue_ml += (barrel.ml_per_barrel * barrel.quantity)
        elif barrel.potion_type == [0,0,0,1]:
            dark_ml += (barrel.ml_per_barrel * barrel.quantity)
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

        if dark_ml != 0:
            connection.execute(sqlalchemy.text('''INSERT INTO ml_ledger (ml_type, change, description)
                                            VALUES ('dark_ml', :change, 'dark ml added from barrel purchase')'''), {"change": dark_ml})

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
        curr_ml_cap = connection.execute(sqlalchemy.text("SELECT curr_ml_cap FROM global_inventory")).scalar()
        num_ml = connection.execute(sqlalchemy.text("SELECT COALESCE(SUM(change), 0) FROM ml_ledger")).scalar()

        capacity = curr_ml_cap - num_ml
        g = gold * .25
        if g > 1000:
            g = 1000
        ordered_barrels = barrel_sizes(wholesale_catalog)

    order_plan = []
    potion_colors = {"RED": False, "GREEN": False, "BLUE": False, "DARK": True}
    
    for barrel in ordered_barrels:
        if g >= barrel.price:
            # Check if the barrel is a new color type
            for color in potion_colors:
                if color in barrel.sku and not potion_colors[color]:
                    potion_colors[color] = True
                    capacity -= barrel.ml_per_barrel 
                    if capacity < 0:
                        break
                    order_plan.append({"sku": barrel.sku, "quantity": 1})
                    g -= barrel.price
                    break  # Move to the next barrel after buying one of a new color

    print("barrels:", order_plan)
    print("gold left:", g)
    return order_plan
    
def barrel_sizes(wholesale_catalog):
    # Filter only medium and large barrels
    filtered_barrels = [barrel for barrel in wholesale_catalog if 'SMALL' in barrel.sku or 'MEDIUM' in barrel.sku or 'LARGE' in barrel.sku]
    # Sort barrels by size and price priority
    ordered_barrels = sorted(
        filtered_barrels,
        key=lambda x: (x.ml_per_barrel, x.price),
        reverse=True
    )
    print("ordering", ordered_barrels)
    return ordered_barrels     