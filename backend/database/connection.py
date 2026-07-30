import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# Load .env
load_dotenv()

# Read MongoDB URI
uri = os.getenv("MONGODB_URI")

if uri and "your_mongodb_connection_string" not in uri:
    try:
        # Connect to MongoDB
        client = MongoClient(uri, server_api=ServerApi("1"))
        # Test connection
        client.admin.command("ping")
        print("[INFO] Connected to MongoDB!")
        db = client["mindmap_ai"]
    except Exception as e:
        print(f"[WARNING] Could not connect to MongoDB: {e}")
        db = None
else:
    print("[INFO] MONGODB_URI not set or using placeholder in .env")
    db = None