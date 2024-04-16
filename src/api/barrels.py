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
        if barrel.potion_type == [100,0,0,0]:
            red_ml += (barrel.ml_per_barrel * barrel.quantity)
        elif barrel.potion_type == [0,100,0,0]:
            green_ml += (barrel.ml_per_barrel * barrel.quantity)
        else:
            blue_ml += (barrel.ml_per_barrel * barrel.quantity)
        price += (barrel.price * barrel.quantity)
    
    # + mL, - gold
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_red_ml = num_red_ml + :red_ml"),
        {"red_ml": red_ml})
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = num_green_ml + :green_ml"),
        {"green_ml": green_ml})
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_blue_ml = num_blue_ml + :blue_ml"),
        {"blue_ml": blue_ml})
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = gold - :price"),
        {"price": price})
            
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")


    return "OK"

# Gets called once a day
# catalog of av. barrels -> which barrels to purchase and how many
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    print(wholesale_catalog)
    with db.engine.begin() as connection:
        red_potions = connection.execute(sqlalchemy.text("SELECT num_red_potions from global_inventory")).scalar()
        green_potions = connection.execute(sqlalchemy.text("SELECT num_green_potions from global_inventory")).scalar()
        blue_potions = connection.execute(sqlalchemy.text("SELECT num_blue_potions from global_inventory")).scalar()
        
        potions = red_potions + green_potions + blue_potions
        gold = connection.execute(sqlalchemy.text("SELECT gold from global_inventory")).scalar()
        barrel_lst = []

        for barrel in wholesale_catalog:
            if potions < 10 and gold >= barrel.price:
                barrel_lst.append({"sku": barrel.sku, "quantity": barrel.quantity})
                gold -= barrel.price
        
        print ("potions = ", potions, ", gold = ",gold)
        print ("barrels:", barrel_lst)


        return barrel_lst
    

    

