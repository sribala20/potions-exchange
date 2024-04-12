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
    barrel_ml = 0
    price = 0
    for barrel in barrels_delivered:
        barrel_ml += (barrel.ml_per_barrel * barrel.quantity)
        price += (barrel.price * barrel.quantity)
    
    # + mL, - gold
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = num_green_ml + :barrel_ml"),
        {"barrel_ml": barrel_ml})
        connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = gold - :price"),
        {"price": price})
            
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    return "OK"

# Gets called once a day
# catalog of av. barrels -> which barrels to purchase and how many
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    print(wholesale_catalog)
    
    for barrel in wholesale_catalog:
        price = barrel.price * barrel.quantity
        with db.engine.begin() as connection:
            potions = connection.execute(sqlalchemy.text("SELECT num_green_potions from global_inventory")).scalar()
            gold = connection.execute(sqlalchemy.text("SELECT gold from global_inventory")).scalar()
            if potions < 10 and gold >= price and barrel.sku == "SMALL_GREEN_BARREL":
                return [ # purchasing one new small green barrel if num_potions < 10 and gold sufficient
                    {
                            "sku": "SMALL_GREEN_BARREL", 
                            "quantity": 1,
                    }
                 ]

    return []
    

    

