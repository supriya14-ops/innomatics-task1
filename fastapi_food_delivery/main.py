from fastapi import FastAPI, Query, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

# -------------------------------
# DATA
# -------------------------------
menu = [
    {"id": 1, "name": "Pizza", "price": 200, "category": "Pizza", "is_available": True},
    {"id": 2, "name": "Burger", "price": 120, "category": "Burger", "is_available": True},
    {"id": 3, "name": "Coke", "price": 50, "category": "Drink", "is_available": True},
    {"id": 4, "name": "Pasta", "price": 180, "category": "Pizza", "is_available": False},
    {"id": 5, "name": "Ice Cream", "price": 90, "category": "Dessert", "is_available": True},
    {"id": 6, "name": "Fries", "price": 80, "category": "Snack", "is_available": True}
]

orders = []
cart = []
order_counter = 1


# -------------------------------
# MODELS
# -------------------------------
class OrderRequest(BaseModel):
    customer_name: str = Field(min_length=2)
    item_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=20)
    delivery_address: str = Field(min_length=10)
    order_type: str = "delivery"


class NewMenuItem(BaseModel):
    name: str = Field(min_length=2)
    price: int = Field(gt=0)
    category: str = Field(min_length=2)
    is_available: bool = True


class CheckoutRequest(BaseModel):
    customer_name: str
    delivery_address: str


# -------------------------------
# HELPER FUNCTIONS
# -------------------------------
def find_menu_item(item_id):
    for item in menu:
        if item["id"] == item_id:
            return item
    return None


def calculate_bill(price, quantity, order_type="delivery"):
    total = price * quantity
    if order_type == "delivery":
        total += 30
    return total


def filter_menu_logic(category, max_price, is_available):
    result = []
    for item in menu:
        if category is not None and item["category"] != category:
            continue
        if max_price is not None and item["price"] > max_price:
            continue
        if is_available is not None and item["is_available"] != is_available:
            continue
        result.append(item)
    return result


# -------------------------------
# DAY 1 - GET APIs
# -------------------------------
@app.get("/")
def home():
    return {"message": "Welcome to Food Delivery App"}


@app.get("/menu")
def get_menu():
    return {"total": len(menu), "items": menu}


@app.get("/menu/summary")
def menu_summary():
    available = sum(1 for i in menu if i["is_available"])
    unavailable = len(menu) - available
    categories = list(set(i["category"] for i in menu))
    return {
        "total": len(menu),
        "available": available,
        "unavailable": unavailable,
        "categories": categories
    }


@app.get("/orders")
def get_orders():
    return {"total_orders": len(orders), "orders": orders}


# -------------------------------
# DAY 3 FILTER
# -------------------------------
@app.get("/menu/filter")
def filter_menu(
    category: Optional[str] = None,
    max_price: Optional[int] = None,
    is_available: Optional[bool] = None
):
    result = filter_menu_logic(category, max_price, is_available)
    return {"count": len(result), "items": result}


# -------------------------------
# DAY 6 SEARCH
# -------------------------------
@app.get("/menu/search")
def search_menu(keyword: str):
    result = [
        i for i in menu
        if keyword.lower() in i["name"].lower()
        or keyword.lower() in i["category"].lower()
    ]
    if not result:
        return {"message": "No items found"}
    return {"total_found": len(result), "items": result}


# -------------------------------
# SORT
# -------------------------------
@app.get("/menu/sort")
def sort_menu(sort_by: str = "price", order: str = "asc"):
    if sort_by not in ["price", "name", "category"]:
        raise HTTPException(400, "Invalid sort field")

    reverse = order == "desc"
    sorted_menu = sorted(menu, key=lambda x: x[sort_by], reverse=reverse)

    return {"sorted_by": sort_by, "order": order, "items": sorted_menu}


# -------------------------------
# PAGINATION
# -------------------------------
@app.get("/menu/page")
def paginate_menu(page: int = 1, limit: int = 3):
    start = (page - 1) * limit
    data = menu[start:start + limit]

    total_pages = (len(menu) + limit - 1) // limit

    return {
        "page": page,
        "limit": limit,
        "total": len(menu),
        "total_pages": total_pages,
        "items": data
    }


# -------------------------------
# COMBINED BROWSE
# -------------------------------
@app.get("/menu/browse")
def browse_menu(
    keyword: Optional[str] = None,
    sort_by: str = "price",
    order: str = "asc",
    page: int = 1,
    limit: int = 4
):
    data = menu

    if keyword:
        data = [i for i in data if keyword.lower() in i["name"].lower()]

    reverse = order == "desc"
    data = sorted(data, key=lambda x: x[sort_by], reverse=reverse)

    start = (page - 1) * limit
    paginated = data[start:start + limit]

    return {
        "total": len(data),
        "page": page,
        "items": paginated
    }


# -------------------------------
# CRUD (DAY 4)
# -------------------------------
@app.post("/menu", status_code=201)
def add_item(item: NewMenuItem):
    for i in menu:
        if i["name"].lower() == item.name.lower():
            raise HTTPException(400, "Item already exists")

    new_item = item.dict()
    new_item["id"] = len(menu) + 1
    menu.append(new_item)
    return new_item


@app.put("/menu/{item_id}")
def update_item(item_id: int, price: Optional[int] = None, is_available: Optional[bool] = None):
    item = find_menu_item(item_id)
    if not item:
        raise HTTPException(404, "Item not found")

    if price is not None:
        item["price"] = price
    if is_available is not None:
        item["is_available"] = is_available

    return item


@app.delete("/menu/{item_id}")
def delete_item(item_id: int):
    item = find_menu_item(item_id)
    if not item:
        raise HTTPException(404, "Item not found")

    menu.remove(item)
    return {"message": "Deleted", "item": item["name"]}


# -------------------------------
# CART (DAY 5)
# -------------------------------
@app.post("/cart/add")
def add_to_cart(item_id: int, quantity: int = 1):
    item = find_menu_item(item_id)
    if not item or not item["is_available"]:
        raise HTTPException(400, "Item not available")

    for c in cart:
        if c["item_id"] == item_id:
            c["quantity"] += quantity
            return {"message": "Updated cart", "cart": cart}

    cart.append({"item_id": item_id, "quantity": quantity})
    return {"message": "Added to cart", "cart": cart}


@app.get("/cart")
def view_cart():
    total = 0
    detailed = []

    for c in cart:
        item = find_menu_item(c["item_id"])
        bill = item["price"] * c["quantity"]
        total += bill

        detailed.append({
            "name": item["name"],
            "quantity": c["quantity"],
            "total": bill
        })

    return {"cart": detailed, "grand_total": total}


@app.delete("/cart/{item_id}")
def remove_cart(item_id: int):
    for c in cart:
        if c["item_id"] == item_id:
            cart.remove(c)
            return {"message": "Removed"}

    raise HTTPException(404, "Item not in cart")


@app.post("/cart/checkout", status_code=201)
def checkout(data: CheckoutRequest):
    global order_counter

    if not cart:
        raise HTTPException(400, "Cart is empty")

    placed_orders = []
    total = 0

    for c in cart:
        item = find_menu_item(c["item_id"])
        bill = item["price"] * c["quantity"]

        order = {
            "order_id": order_counter,
            "customer": data.customer_name,
            "item": item["name"],
            "quantity": c["quantity"],
            "total": bill
        }

        orders.append(order)
        placed_orders.append(order)

        total += bill
        order_counter += 1

    cart.clear()

    return {"orders": placed_orders, "grand_total": total}


# -------------------------------
# VARIABLE ROUTE (LAST)
# -------------------------------
@app.get("/menu/{item_id}")
def get_item(item_id: int):
    item = find_menu_item(item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    return item