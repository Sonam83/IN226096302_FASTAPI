from fastapi import FastAPI,Query
from pydantic import BaseModel, Field
from typing import Optional, List #Ass 2
 
app = FastAPI() #variable or object

# ================= PYDANTIC MODEL =================
class OrderRequest(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=100)
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=100)
    delivery_address: str = Field(..., min_length=10)

# _____________________________ Ass 2 : pydantic model ___________________________
class CustomerFeedback(BaseModel):
    customer_name: str = Field(...,min_length=2, max_length=100)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)

# ________________________Ass 2 : pydantic model ____________________________________
class OrderItem(BaseModel):
    product_id: int=Field(...,gt=0)
    quantity: int=Field(...,gt=0, le=50)

class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: List[OrderItem] = Field(...,min_items=1)
 
# ── Temporary data — acting as our database for now ────────── 1
products = [
    {'id': 1, 'name': 'Wireless Mouse', 'price': 499,  'category': 'Electronics', 'in_stock': True },
    {'id': 2, 'name': 'Notebook',       'price':  99,  'category': 'Stationery',  'in_stock': True },
    {'id': 3, 'name': 'USB Hub',         'price': 799, 'category': 'Electronics', 'in_stock': False},
    {'id': 4, 'name': 'Pen Set',          'price':  49, 'category': 'Stationery',  'in_stock': True },
    {'id': 5, 'name': 'Laptop Stand',          'price':  1299, 'category': 'Electronics',  'in_stock': True },
    {'id': 6, 'name': 'Mechanical Keyboard',          'price':  2499, 'category': 'Electronics',  'in_stock': True },
    {'id': 7, 'name': 'Webcam',          'price':  1899, 'category': 'Electronics',  'in_stock': False },
]

# Ass 2
orders = []
feedback=[]
order_counter = 1

# _______________--Class work : Helper Functions ________________________
# ================= HELPER FUNCTIONS =================

def find_product(product_id: int):
    """Search product list by ID"""
    for p in products:
        if p["id"] == product_id:
            return p
    return None


def calculate_total(product: dict, quantity: int) -> int:
    """Multiply price by quantity and return total"""
    return product["price"] * quantity


def filter_products_logic(category=None, min_price=None, max_price=None, in_stock=None):
    """Apply filters and return matching products"""
    result = products

    if category is not None:
        result = [p for p in result if p["category"] == category]

    if min_price is not None:
        result = [p for p in result if p["price"] >= min_price]

    if max_price is not None:
        result = [p for p in result if p["price"] <= max_price]

    if in_stock is not None:
        result = [p for p in result if p["in_stock"] == in_stock]

    return result

 
# ── Endpoint 0 — Home ──────────────────────────────────────── 2
@app.get('/')  #decorator : get method : to get home page
def home():
    return {'message': 'Welcome to our E-commerce API'}

# ----Assignment 1 part 3 ----------store summary endpoint
@app.get("/store/summary")
def store_summary():
    in_stock_count=len([p for p in products if p["in_stock"]])
    out_stock_count=len(products) - in_stock_count
    categories=list(set([p["category"] for p in products]))
    return {"store_name":"My E-commerce Store","total_products":len(products),"in_stock":in_stock_count,
    "out_of_stock":out_stock_count,"categories":categories,}
 
# ── Endpoint 1 — Return all products ────────────────────────── 3
@app.get('/products')  #decorator : to get all products on UI
def get_all_products():
    return {'products': products, 'total': len(products)}

# --------endpoint : Assignment 1 part 5 offer deals-----------------------
@app.get("/products/deals")
def get_deals():
    cheapest=min(products,key=lambda p:p["price"])
    expensive=max(products,key=lambda p:p["price"])
    return {"best_deal":cheapest,"premium_pick":expensive,}

# --------endpoint : Assignment 1 part 4 keyword search-----------------------
@app.get("/products/search/{keyword}")
def search_products(keyword:str):
    results=[p for p in products if keyword.lower() in p["name"].lower()]
    if not results:
        return {"message":"No products matched your search"}
    return {"keyword":keyword,"results":results,"total_matches":len(results)}

# --------- Endpoint : to filter product ---------------------- 4
@app.get('/products/filter')
def filter_products(
    category:  str  = Query(None, description='Electronics or Stationery'),
    max_price: int  = Query(None, description='Maximum price'),
    in_stock:  bool = Query(None, description='True = in stock only'),
    min_price: int = Query(None, description='Minimum price') #day 2 assignment
):
    result = products          # start with all products
 
    if category:
        result = [p for p in result if p['category'] == category]
 
    if max_price:
        result = [p for p in result if p['price'] <= max_price]
 
    if in_stock is not None:
        result = [p for p in result if p['in_stock'] == in_stock]

    if min_price: #day 2 assignment
        result=[p for p in result if p['price'] >= min_price]
 
    return {'filtered_products': result, 'count': len(result)}

#-------------Endpoint Assignment 1 2nd part----------in stock products
@app.get("/products/instock")
def get_instock():
    
        available=[p for p in products if p["in_stock"]==True]
        return {"in_stock_products":available,"count":len(available)}

# _____________________ Ass 2 : Endpoint products summary ______________________________________
@app.get("/products/summary")
def product_summary():
    in_stock = [p for p in products if p["in_stock"]]
    out_stock = [p for p in products if not p["in_stock"]]
    expensive = max(products, key=lambda p:p["price"])
    cheapest = min(products, key=lambda p:p["price"])
    categories = list(set(p["category"] for p in products))
    return {
        "total_products": len(products),
        "in_stock_count": len(in_stock),
        "out_of_stock_count": len(out_stock),
        "most_expensive": {"name":expensive["name"],"price": expensive["price"]},
        "cheapest": {"name": cheapest["name"], "price": cheapest["price"]},
        "categories": categories,
    }

 
# ── Endpoint 2 — Return one product by its ID ────────────────── 5
@app.get('/products/{product_id}')  # decorator : to get specific product
def get_product(product_id: int):
    for product in products:
        if product['id'] == product_id:
            return {'product': product}
    return {'error': 'Product not found'}

# ______________________ Ass 2 end point for only product name and price_______________________________
@app.get('/products/{product_id}/price')
def get_product_price(product_id: int):
    for product in products:
        if product["id"]==product_id:
            return {"name":product["name"],"price":product["price"]}
    return {"error": "Product not found"}

# ----Endpoint Assignment 1 ----to get only required category
@app.get('/products/category/{category_name}') #decorator : to get req category and products based on category name
def get_by_category(category_name: str):
    result=[p for p in products if p["category"]==category_name]
    if not result:
        return {"error":"No products found in this category"}
    return {"category":category_name,"products":result,"total":len(result)}
#_____________________________Class work :Orders Endpoint_____________________
# -------- Place Order --------
@app.post("/orders")
def place_order(order_data: OrderRequest):
    global order_counter

    product = find_product(order_data.product_id)

    if not product:
        return {"error": "Product not found"}

    if not product["in_stock"]:
        return {"error": f"{product['name']} is out of stock"}

    total = calculate_total(product, order_data.quantity)

    order = {
        "order_id": order_counter,
        "customer_name": order_data.customer_name,
        "product": product["name"],
        "quantity": order_data.quantity,
        "delivery_address": order_data.delivery_address,
        "total_price": total,
        "status": "pending" #ass 2 earlier it was confirmed
    }

    orders.append(order)
    order_counter += 1

    return {
        "message": "Order placed successfully",
        "order": order
    }


# -------- Get All Orders --------
@app.get("/orders")
def get_all_orders():
    return {
        "orders": orders,
        "total_orders": len(orders)
    }

# ______________________Ass 2 : Endpoint - Bulk order ________________________
@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):
    confirmed, failed, grand_total=[],[],0
    for item in order.items:
        product=next((p for p in products if p["id"]== item.product_id), None)
        if not product:
            failed.append({"product_id":item.product_id,"reason":"Product not found"})
        elif not product["in_stock"]:
            failed.append({"product_id":item.product_id,"reason":f"{product['name']} is out of stock"})
        else:
            subtotal=product["price"]*item.quantity
            grand_total+=subtotal
            confirmed.append({"product":product["name"],"qty":item.quantity,"subtotal":subtotal})
    return {"company":order.company_name,"confirmed":confirmed,"failed":failed,"grand_total":grand_total}

#______________________--Ass 2 : End point order id______________________________
@app.get("/orders/{order_id}")
def get_order(order_id:int):
    for order in orders:
        if order["order_id"]==order_id:
            return {"order":order}
    return {"error":"Order not found"}

# _____________________Ass 2 : Patch end point __________________________________
@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id : int):
    for order in orders:
        if order["order_id"]==order_id:
            order["status"]="confirmed"
            return {"message":"Order Confirmed","order":order}
    return {"error":"Order not found"}


# _____________-Ass 2 bottom feedback endpoint ______________________________--
@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):
    feedback.append(data.dict())
    return {
        "message": "Feedback submitted successfully",
        "feedback": data.dict(),
        "total_feedback":len(feedback),
    }



