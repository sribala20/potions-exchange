from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
import sqlalchemy
from src import database as db

 
router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/reset")
def reset():
    """
    Reset the game state. Gold goes to 100, all potions are removed from
    inventory, and all barrels are removed from inventory. Carts are all reset.
    """

    #truncate deletes data within table but not table itself
    with db.engine.begin() as connection:
        connection.execute(sqlalchemy.text("TRUNCATE gold_ledger")) 
        connection.execute(sqlalchemy.text('''INSERT INTO gold_ledger (change, description)
                                           VALUES (100, 'reset state')'''))
        connection.execute(sqlalchemy.text("TRUNCATE ml_ledger")) 
        connection.execute(sqlalchemy.text("TRUNCATE potion_ledger")) 
    return "OK"

