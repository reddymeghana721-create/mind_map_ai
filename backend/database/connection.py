import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# Load .env
load_dotenv()

# Read MongoDB URI
uri = os.getenv("MONGODB_URI")

client = None
db = None

if uri:
    try:
        client = MongoClient(uri, server_api=ServerApi("1"), serverSelectionTimeoutMS=3000)
        client.admin.command("ping")
        print("[OK] Connected to MongoDB!")
        db = client["mindmap_ai"]
    except Exception as e:
        print(f"[WARNING] MongoDB Connection Failed ({e}). Falling back to local disk storage.")
        db = None
else:
    print("[WARNING] MONGODB_URI not found in .env. Falling back to local disk storage.")