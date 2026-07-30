from database.connection import db

if db is not None:
    print("Database Name:", db.name)
    print("MongoDB Connected Successfully!")
else:
    print("MongoDB not connected. Please set MONGODB_URI in backend/.env")