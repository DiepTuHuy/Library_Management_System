from pymongo import MongoClient

# MongoDB Atlas Connection
MONGODB_URI = "mongodb+srv://dieptuhuy80:Hitori123@lms.wpuvhhb.mongodb.net/library_db"

def get_db():
    client = MongoClient(MONGODB_URI)
    return client["LMD_DB"]

def init_db():
    """Initialize database and return database object"""
    client = MongoClient(MONGODB_URI)
    db = client["LMD_DB"]
    return db