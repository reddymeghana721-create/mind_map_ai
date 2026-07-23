import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# Load .env
load_dotenv()

# Read MongoDB URI
uri = os.getenv("MONGODB_URI")

if not uri:
    raise Exception("MONGODB_URI not found in .env")

# Connect to MongoDB
client = MongoClient(uri, server_api=ServerApi("1"))

# Test connection
client.admin.command("ping")

print("✅ Connected to MongoDB!")

# Database
db = client["mindmap_ai"]