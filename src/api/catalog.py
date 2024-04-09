from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])

def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    green_count = 0
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_green_potions from global_inventory"))
        green_count = result.scalar()
    
    return [
            {
                "sku": "GREEN_POTION_0",
                "name": "green potion",
                "quantity": green_count,
                "price": 50,
                "potion_type": [100, 0, 0, 0],
            }
        ]
