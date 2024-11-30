from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from database import users_collection
from events import publish_event
from bson import ObjectId
from typing import Optional

app = FastAPI()

class UserCreate(BaseModel):
    email: EmailStr
    delivery_address: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    delivery_address: Optional[str] = None

@app.post("/users")
def create_user(user: UserCreate):
    # Insert a new user and return the MongoDB-generated _id
    result = users_collection.insert_one(user.dict())
    return {"message": "User created successfully", "user_id": str(result.inserted_id)}

@app.put("/users/{user_id}")
def update_user(user_id: str, user: UserUpdate):
    # Validate and convert string to ObjectId
    try:
        mongo_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    # Build the update dictionary dynamically
    update_data = {key: value for key, value in user.dict().items() if value is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    # Perform the update
    result = users_collection.update_one({"_id": mongo_id}, {"$set": update_data})

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    # Publish update event
    publish_event("user_updated", {"user_id": user_id, **update_data})
    return {"message": "User updated successfully"}

@app.get("/users/{user_id}")
def get_user(user_id: str):
    # Retrieve a user by ID
    try:
        mongo_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    user = users_collection.find_one({"_id": mongo_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Convert MongoDB ObjectId to string for the response
    user["_id"] = str(user["_id"])
    return user
