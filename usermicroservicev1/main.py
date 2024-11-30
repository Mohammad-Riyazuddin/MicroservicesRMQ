from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import users_collection
from events import publish_event
from bson import ObjectId

app = FastAPI()

class User(BaseModel):
    user_id: str
    email: str
    delivery_address: str

@app.post("/users")
def create_user(user: User):
    user_id = users_collection.insert_one(user.dict()).inserted_id
    return {"message": "User created successfully", "user_id": str(user_id)}

@app.put("/users/{user_id}")
def update_user(user_id: str, user: User):
    # Convert string to ObjectId for MongoDB _id
    try:
        user_id = user_id
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid _id format")

    # Perform the update using MongoDB's _id
    result = users_collection.update_one(
        {"user_id": user_id},  # Find the document by MongoDB _id
        {"$set": {
            "user_id": user.user_id,
            "email": user.email, 
            "delivery_address": user.delivery_address
        }}
    )

    # Check if a document was updated
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    # Publish the event that the user was updated
    publish_event(
        "user_updated",
        {   
            "user_id": user.user_id,
            "email": user.email,
            "delivery_address": user.delivery_address
        }
    )

    return {"message": "User updated successfully"}
