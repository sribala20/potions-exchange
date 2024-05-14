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
        stash = connection.execute(sqlalchemy.text("""SELECT sku, name, price, type, COALESCE(SUM(potion_ledger.change), 0) AS quantity
                                                   FROM potion_ledger
                                                   INNER JOIN potions ON potion_ledger.potion_sku = potions.sku
                                                   GROUP BY potions.sku
                                                   """)) # gets quantities by sku 
        
        limit = 0
        for row in stash:
            limit += 1
            if limit == 7: break
            catalog_lst.append(
                {
                    "sku": row.sku,
                    "name": row.name,
                    "quantity": row.quantity,
                    "price": row.price,
                    "potion_type": row.type,
                })
    
    return catalog_lst
