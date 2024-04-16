from fastapi import APIRouter
import sqlalchemy
from src import database as db

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])

def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    catalog_lst = []
    with db.engine.begin() as connection:
        red_count = connection.execute(sqlalchemy.text("SELECT num_red_potions from global_inventory")).scalar()
        green_count = connection.execute(sqlalchemy.text("SELECT num_green_potions from global_inventory")).scalar()
        blue_count = connection.execute(sqlalchemy.text("SELECT num_blue_potions from global_inventory")).scalar()
    
    if red_count > 0:
        catalog_lst.append(
            {
                "sku": "RED_POTION_0",
                "name": "red potion",
                "quantity": red_count,
                "price": 5,
                "potion_type": [100, 0, 0, 0],
            })
        
    if green_count > 0:
        catalog_lst.append(
            {
                "sku": "GREEN_POTION_0",
                "name": "green potion",
                "quantity": green_count,
                "price": 10,
                "potion_type": [0, 100, 0, 0],
            })
    
    if blue_count > 0:
        catalog_lst.append(
            {
                "sku": "BLUE_POTION_0",
                "name": "blue potion",
                "quantity": blue_count,
                "price": 20,
                "potion_type": [0, 0, 100, 0],
            })
    
    
    return catalog_lst
