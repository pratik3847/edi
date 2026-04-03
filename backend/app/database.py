"""
Database Initialization Module
Sets up the MongoDB connection and provides access to collections across the app.
"""
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

client = MongoClient(MONGO_URI)
db = client["edi_platform"]

users_collection = db["users"]
sessions_collection = db["sessions"]
