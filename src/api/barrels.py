from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db     

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
    price = 0
    
    for barrel in barrels_delivered:
        price += (barrel.price * barrel.quantity)
        if barrel.potion_type == [1,0,0,0]:
            red_ml += (barrel.ml_per_barrel * barrel.quantity)
        elif barrel.potion_type == [0,1,0,0]:
            green_ml += (barrel.ml_per_barrel * barrel.quantity)
        elif barrel.potion_type == [0,0,1,0]:
            blue_ml += (barrel.ml_per_barrel * barrel.quantity)
        else:
            raise Exception("invalid potion type.")
        
    # + mL, - gold
    with db.engine.begin() as connection:
        # try: insert into processed(job_id, type), values order_id and barrels | except: integrityerror
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = num_red_ml + :red_ml"),
        {"red_ml": red_ml})
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = num_green_ml + :green_ml"),
        {"green_ml": green_ml})
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_ml = num_blue_ml + :blue_ml"),
        {"blue_ml": blue_ml})
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = gold - :price"),
        {"price": price})
            
    print(f"gold_paid: {price}, order_id: {order_id}") 


    return "OK"
    
# Gets called once a day
# catalog of av. barrels -> which barrels to purchase and how many
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    print(wholesale_catalog)

    ordered_barrels = barrel_sizes(wholesale_catalog)

    with db.engine.begin() as connection:
        # spend half gold on barrels
        gold = connection.execute(sqlalchemy.text("SELECT gold from global_inventory")).scalar()//2

    order_plan = []
    for barrel in ordered_barrels:
        if gold < barrel.price:
            break
        order_plan.append({"sku": barrel.sku, "quantity": 1})
        gold -= barrel.price
        
    print ("barrels:", order_plan)
    return order_plan
    

# def best_barrels(barrel_lst: list[Barrel]):
#     sorted(barrel_lst, key=lambda barrel: barrel.ml_per_barrel / barrel.price, reverse=True)

# organizes barrels from smallest to largest, allows to iterate and buy smalls of each color first. 
def barrel_sizes(wholesale_catalog: list[Barrel]):
    mini_barrels = []
    small_barrels = []
    large_barrels = []

    for barrel in wholesale_catalog:
        if 'MINI' in barrel.sku:
            mini_barrels.append(barrel)
        elif 'SMALL' in barrel.sku:
            small_barrels.append(barrel)
        elif 'LARGE' in barrel.sku:
            large_barrels.append(barrel)
        else:
            raise Exception("Rand size.")

    ordered_barrels = mini_barrels + small_barrels + large_barrels
    print(ordered_barrels)
    return ordered_barrels   


'''
[Barrel(sku='SMALL_RED_BARREL', ml_per_barrel=500, potion_type=[1, 0, 0, 0], price=100, quantity=10), 
Barrel(sku='SMALL_GREEN_BARREL', ml_per_barrel=500, potion_type=[0, 1, 0, 0], price=100, quantity=10), 
Barrel(sku='SMALL_BLUE_BARREL', ml_per_barrel=500, potion_type=[0, 0, 1, 0], price=120, quantity=10), 
Barrel(sku='MINI_RED_BARREL', ml_per_barrel=200, potion_type=[1, 0, 0, 0], price=60, quantity=1), 
Barrel(sku='MINI_GREEN_BARREL', ml_per_barrel=200, potion_type=[0, 1, 0, 0], price=60, quantity=1), 
Barrel(sku='MINI_BLUE_BARREL', ml_per_barrel=200, potion_type=[0, 0, 1, 0], price=60, quantity=1), 
Barrel(sku='LARGE_DARK_BARREL', ml_per_barrel=10000, potion_type=[0, 0, 0, 1], price=750, quantity=10), 
Barrel(sku='LARGE_BLUE_BARREL', ml_per_barrel=10000, potion_type=[0, 0, 1, 0], price=600, quantity=30), 
Barrel(sku='LARGE_GREEN_BARREL', ml_per_barrel=10000, potion_type=[0, 1, 0, 0], price=400, quantity=30), 
Barrel(sku='LARGE_RED_BARREL', ml_per_barrel=10000, potion_type=[1, 0, 0, 0], price=500, quantity=30)]'''
