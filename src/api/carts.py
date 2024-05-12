from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src.api import auth
from enum import Enum
import sqlalchemy
from src import database as db
import random

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)

class search_sort_options(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"

class search_sort_order(str, Enum):
    asc = "ASC"
    desc = "DESC"   

@router.get("/search/", tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: search_sort_options = search_sort_options.timestamp,
    sort_order: search_sort_order = search_sort_order.desc,
):
    vars = {}
    sql = """SELECT 
            cart_items.id AS line_item_id, 
            cart_items.potion_sku AS item_sku,
            carts.customer_name AS customer_name,
            potions.price * cart_items.quantity AS line_item_total,
            cart_items.timestamp AS timestamp
        FROM cart_items
        JOIN carts ON carts.id = cart_items.id
        JOIN potions ON potions.sku = cart_items.potion_sku
    """

    # filter by customer name and potion sku
    if len(customer_name) > 0:
        vars['%' + customer_name] = "customer"
        sql += "WHERE customer_name ILIKE :customer" #ilike helps with pattern matching and filtering, % matches 0+ chars
    if len(potion_sku) > 0:
        vars['%' + potion_sku] = "sku"
        if len(customer_name) == 0:
            sql += "WHERE item_sku ILIKE :sku"
        else:
            sql += "AND item_sku ILIKE :sku"

    # sorting logic
    print (sort_col)
    sql +=  " ORDER BY " + sort_col + " " + sort_order + " "
    # ex - ORDER BY timestamp DESC

    #paging
    if len(search_page == 0):
        search_page = 0
        previous = ""
    else: 
        previous = str(search_page) - 1 # no prev when page = 0
    next = str(int(search_page) + 1)
    offset = int(search_page) * 5 # 0 if page is 0
    vars[offset] = "offset"
    sql += "LIMIT 5 OFFSET :offset"


    with db.engine.begin() as connection:       
        result = connection.execute(sqlalchemy.text(),[vars])
    
    filtered_res = []
    for row in result:
        filtered_res.append({
            "line_item_id": row.line_item_id,
                "item_sku": row.item_sku,
                "customer_name": row.customer_name,
                "line_item_total": row.line_item_total,
                "timestamp":row.timestamp,  
        })

    return {
        "previous": previous,
        "next": next,
        "results": filtered_res,
    }


    """
    Search for cart line items by customer name and/or potion sku.

    Customer name and potion sku filter to orders that contain the 
    string (case insensitive). If the filters aren't provided, no
    filtering occurs on the respective search term.

    Search page is a cursor for pagination. The response to this
    search endpoint will return previous or next if there is a
    previous or next page of results available. The token passed
    in that search response can be passed in the next search request
    as search page to get that page of results.

    Sort col is which column to sort by and sort order is the direction
    of the search. They default to searching by timestamp of the order
    in descending order.

    The response itself contains a previous and next page token (if
    such pages exist) and the results as an array of line items. Each
    line item contains the line item id (must be unique), item sku, 
    customer name, line item total (in gold), and timestamp of the order.
    Your results must be paginated, the max results you can return at any
    time is 5 total line items.
    """

    # customer name and potion sku filters 

    return {
        "previous": "",
        "next": "",
        "results": [
            {
                "line_item_id": 1,
                "item_sku": "1 oblivion potion",
                "customer_name": "Scaramouche",
                "line_item_total": 50,
                "timestamp": "2021-01-01T00:00:00Z",
            }
        ],
    }


class Customer(BaseModel):
    customer_name: str
    character_class: str
    level: int 

@router.post("/visits/{visit_id}")
def post_visits(visit_id: int, customers: list[Customer]):
    """
    Which customers visited the shop today?
    """
    print(customers)

    return "OK"


@router.post("/")
def create_cart(new_cart: Customer):
    with db.engine.begin() as connection:
        cart_id = connection.execute(sqlalchemy.text("INSERT INTO carts (customer_name, character_class, level) VALUES (:customer_name, :character_class, :level) RETURNING id"),
                [{"customer_name": new_cart.customer_name, "character_class": new_cart.character_class, "level": new_cart.level}]).scalar()
    
    print(f"cart_id: {cart_id} customer_name: {new_cart.customer_name} character_class: {new_cart.character_class} level: {new_cart.level}")
    return {"cart_id": cart_id}


class CartItem(BaseModel):
    quantity: int

# adds items to cart
@router.post("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ """
    with db.engine.begin() as connection:       
        connection.execute(
            sqlalchemy.text("INSERT INTO cart_items (id, potion_sku, quantity) VALUES (:cart_id, :potionId, :quantity)"),
            [{"cart_id": cart_id, "potionId": item_sku, "quantity": cart_item.quantity}]
        )
    return "OK"


class CartCheckout(BaseModel):
    payment: str

# -potions, +gold
@router.post("/{cart_id}/checkout")
def checkout(cart_id: int, cart_checkout: CartCheckout):

    with db.engine.begin() as connection:
        sku = connection.execute(sqlalchemy.text("SELECT potion_sku from cart_items WHERE id = :cart_id"), [{"cart_id": cart_id}]).scalar()
        quant = connection.execute(sqlalchemy.text("SELECT quantity from cart_items WHERE id = :cart_id"), [{"cart_id": cart_id}]).scalar()
        
        connection.execute(sqlalchemy.text(
                    """
                    INSERT INTO potion_ledger (change, potion_sku, description)
                    VALUES (
                        :quantity, :sku, 'potion sold')
                    """
                    ), {"sku": sku, "quantity": -1 * quant})
        
        payment = int(cart_checkout.payment)

        connection.execute(sqlalchemy.text('''INSERT INTO gold_ledger (change, description)
                                           VALUES (:change, 'potions sold')'''), {"change": payment})

    return {"total_potions_bought": quant, "total_gold_paid": payment}
