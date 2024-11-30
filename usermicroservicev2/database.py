from pymongo import MongoClient

client = MongoClient("mongodb+srv://riozon1234:U8EEXYVLPjuOKouE@cluster0.x9xlj.mongodb.net/")
db = client["UsersDB"]
users_collection = db["users"]