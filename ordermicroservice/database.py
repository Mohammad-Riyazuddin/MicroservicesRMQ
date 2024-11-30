from pymongo import MongoClient

client = MongoClient("mongodb+srv://riozon1234:U8EEXYVLPjuOKouE@cluster0.x9xlj.mongodb.net/")
db = client["ordersDB"]
orders_collection = db["orders"]
