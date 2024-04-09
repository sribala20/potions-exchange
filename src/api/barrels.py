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
    for barrel in barrels_delivered:
        # + mL, - gold
        with db.engine.begin() as connection:
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET num_green_ml = num_green_ml + (%d)", (barrel.ml_per_barrel,)))
            connection.execute(sqlalchemy.text("UPDATE global_inventory SET gold = gold - (%d)", (barrel.price,)))
            
    print(f"barrels delievered: {barrels_delivered} order_id: {order_id}")

    return "OK"

# Gets called once a day
# catalog of av. barrels -> which barrels to purchase and how many
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    new_barrel = 0
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_green_potions from global_inventory"))
        potions = result.scalar
        if potions < 10:
            new_barrel = 1  

    print(wholesale_catalog)

    return [ # purchasing one new small green barrel if num_potions < 10
        {
            "sku": "SMALL_GREEN_BARREL", 
            "quantity": new_barrel,
        }
    ]

