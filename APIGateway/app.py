import random
import json
import requests
from fastapi import FastAPI, Request

# Load configuration (percentage P)
with open("config.json", "r") as config_file:
    config = json.load(config_file)

P = config.get("p")  # Percentage of traffic to route to v1

# Define FastAPI app
app = FastAPI()

# Define the base URLs of the microservices (v1 and v2)
V1_URL = "http://usermicroservicev1:8000"  # Legacy microservice
V2_URL = "http://usermicroservicev2:8000"  # New microservice
ORDER_URL = "http://ordermicroservice:8000"  # Order microservice

# Function to route the request to the backend
def route_request_to_backend(url: str, path: str, method: str, data: dict = None):
    """Helper function to route the request to the backend (v1 or v2)"""
    if method == "POST":
        response = requests.post(f"{url}/{path}", json=data)
    elif method == "PUT":
        response = requests.put(f"{url}/{path}", json=data)
    else:
        response = requests.get(f"{url}/{path}")
    return response.json()

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT"])
async def gateway(path: str, request: Request):
    """Main gateway function to handle incoming requests and route them to either v1 or v2"""
    
    method = request.method
    data = await request.json() if method in ["POST", "PUT"] else None
    
    if path.startswith("orders/"):
        # Route to the order microservice
        response = route_request_to_backend(ORDER_URL, path, method, data)
    else:
        # Randomly decide whether to route to v1 or v2 based on percentage P
        if random.randint(1, 100) <= P:
            # Route to v1 (legacy)
            response = route_request_to_backend(V1_URL, f"{path}", method, data)
        else:
            # Route to v2 (new)
            response = route_request_to_backend(V2_URL, f"{path}", method, data)
    
    return response
