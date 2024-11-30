from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from bson import ObjectId
from database import orders_collection


app = FastAPI()


# Pydantic model for Order Items
class OrderItem(BaseModel):
    item_name: str
    quantity: int


# Pydantic model for Order
class Order(BaseModel):
    user_id: str
    items: list[OrderItem]
    email: str
    delivery_address: str
    status: str


# Utility function to handle ObjectId and MongoDB-specific serialization
def convert_objectid_to_str(data):
    if isinstance(data, list):
        return [convert_objectid_to_str(doc) for doc in data]
    elif isinstance(data, dict):
        return {k: convert_objectid_to_str(v) for k, v in data.items()}
    elif isinstance(data, ObjectId):
        return str(data)
    elif isinstance(data, dict) and "$numberInt" in data:  # Handle MongoDB integer serialization
        return int(data["$numberInt"])
    elif isinstance(data, dict) and "$oid" in data:  # Handle MongoDB ObjectId
        return str(data["$oid"])
    else:
        return data


@app.post("/orders")
def create_order(order: Order):
    # Insert the order into the database
    order_dict = order.dict()
    order_dict["items"] = [
        {"item_name": item.item_name, "quantity": item.quantity}
        for item in order.items
    ]
    order_id = orders_collection.insert_one(order_dict).inserted_id
    return {"message": "Order created successfully", "order_id": str(order_id)}


@app.get("/orders")
def get_orders(status: str = None):
    # Query for orders based on the status, if provided
    query = {"status": status} if status else {}
    orders = list(orders_collection.find(query))
    # Convert ObjectId and MongoDB-specific fields to string/int in the response
    orders = convert_objectid_to_str(orders)
    return orders


@app.put("/orders/{order_id}/status")
def update_order_status(order_id: str, order_status: str):
    # Convert order_id to ObjectId
    try:
        order_id_object = ObjectId(order_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid order_id format")

    # Update the order's status in the database
    result = orders_collection.update_one(
        {"_id": order_id_object}, {"$set": {"status": order_status}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")

    return {"message": "Order status updated successfully"}
