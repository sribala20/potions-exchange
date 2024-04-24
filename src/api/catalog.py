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
        stash = connection.execute(sqlalchemy.text("SELECT sku, name, quantity, price, type from potions"))
        for row in stash:
            catalog_lst.append(
                {
                    "sku": row.sku,
                    "name": row.name,
                    "quantity": row.quantity,
                    "price": row.price,
                    "potion_type": row.type,
                })
    
    return catalog_lst
