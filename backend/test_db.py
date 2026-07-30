from database.connection import db

if db is not None:
    print("Database Name:", db.name)
    print("[OK] MongoDB Connected Successfully!")
else:
    print("[INFO] MongoDB is currently offline or not configured. App will use disk storage.")