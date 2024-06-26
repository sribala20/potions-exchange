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
                                                   GROUP BY potions.sku HAVING COALESCE(SUM(potion_ledger.change), 0) > 0
                                                   ORDER BY name ASC, quantity DESC
                                                   """)) # gets quantities by sku 
        
        limit = 0
        for row in stash:
            limit += 1
            if limit == 6: break
            if row.quantity > 0:
                catalog_lst.append(
                    {
                        "sku": row.sku,
                        "name": row.name,
                        "quantity": row.quantity,
                        "price": row.price,
                        "potion_type": row.type,
                    })
            
    print(catalog_lst)
    
    return catalog_lst
