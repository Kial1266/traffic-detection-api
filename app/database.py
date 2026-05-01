from motor.motor_asyncio import AsyncIOMotorClient
import os

# Ganti dengan connection string MongoDB kamu (Lokal atau Atlas)
MONGO_DETAILS = "mongodb://localhost:27017"

client = AsyncIOMotorClient(MONGO_DETAILS)
database = client.traffic_db
collection = database.get_collection("traffic_logs")