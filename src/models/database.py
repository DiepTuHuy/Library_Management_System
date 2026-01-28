from pymongo import MongoClient
from datetime import datetime

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

def seed_default_users(db):
    """
    Seed default admin and librarian users into MongoDB
    Only creates them if they don't exist
    
    Args:
        db: MongoDB database object
    
    Returns:
        dict: {
            "admin_created": bool,
            "librarian_created": bool,
            "message": str
        }
    """
    from .user import User
    
    users_collection = db["users"]
    results = {
        "admin_created": False,
        "librarian_created": False,
        "message": ""
    }
    
    # DEFAULT ADMIN USER
    admin_email = "admin@library.system"
    admin_exists = users_collection.find_one({"email": admin_email})
    
    if not admin_exists:
        admin_user = User(
            name="Administrator",
            email=admin_email,
            password="admin123",
            role="admin"
        )
        admin_user.save(db)
        results["admin_created"] = True
        print("[+] Admin user seeded to database")
    else:
        print("[+] Admin user already exists in database")
    
    # DEFAULT LIBRARIAN USER
    librarian_email = "librarian@library.system"
    librarian_exists = users_collection.find_one({"email": librarian_email})
    
    if not librarian_exists:
        librarian_user = User(
            name="Librarian",
            email=librarian_email,
            password="librarian123",
            role="librarian"
        )
        librarian_user.save(db)
        results["librarian_created"] = True
        print("[+] Librarian user seeded to database")
    else:
        print("[+] Librarian user already exists in database")
    
    return results

def init_database_with_seed():
    """
    Initialize database with seeded default users and sample books
    Call this on application startup
    
    Returns:
        dict: Database initialization results
    """
    db = init_db()
    
    print("\n" + "="*80)
    print("[*] DATABASE INITIALIZATION")
    print("="*80)
    
    # Create indexes for better query performance
    users_collection = db["users"]
    users_collection.create_index("email", unique=True, sparse=True)
    
    books_collection = db["books"]
    books_collection.create_index("isbn", unique=True, sparse=True)
    books_collection.create_index("book_id", unique=True, sparse=True)
    print("[+] Database indexes created")
    
    # Seed default users
    seed_results = seed_default_users(db)
    
    # Seed sample books
    seed_sample_books(db)
    
    print("="*80 + "\n")
    
    return seed_results

def seed_sample_books(db):
    """
    Seed sample books into MongoDB for testing
    Only creates them if collection is empty
    
    Args:
        db: MongoDB database object
    """
    books_collection = db["books"]
    
    # Check if books already exist
    if books_collection.count_documents({"is_active": True}) > 0:
        print("[+] Books already exist in database")
        return
    
    sample_books = [
        {
            "book_id": "BOOK001",
            "title": "The Great Gatsby",
            "author": "F. Scott Fitzgerald",
            "publisher": "Scribner",
            "year": 1925,
            "category": "Fiction",
            "isbn": "978-0743273565",
            "quantity": 5,
            "available_quantity": 5,
            "status": "Available",
            "created_at": datetime.utcnow(),
            "is_active": True
        },
        {
            "book_id": "BOOK002",
            "title": "To Kill a Mockingbird",
            "author": "Harper Lee",
            "publisher": "J.B. Lippincott",
            "year": 1960,
            "category": "Fiction",
            "isbn": "978-0061120084",
            "quantity": 4,
            "available_quantity": 4,
            "status": "Available",
            "created_at": datetime.utcnow(),
            "is_active": True
        },
        {
            "book_id": "BOOK003",
            "title": "1984",
            "author": "George Orwell",
            "publisher": "Secker & Warburg",
            "year": 1949,
            "category": "Fiction",
            "isbn": "978-0451524935",
            "quantity": 3,
            "available_quantity": 2,
            "status": "Available",
            "created_at": datetime.utcnow(),
            "is_active": True
        },
        {
            "book_id": "BOOK004",
            "title": "Pride and Prejudice",
            "author": "Jane Austen",
            "publisher": "T. Egerton",
            "year": 1813,
            "category": "Romance",
            "isbn": "978-0141439518",
            "quantity": 2,
            "available_quantity": 2,
            "status": "Available",
            "created_at": datetime.utcnow(),
            "is_active": True
        },
        {
            "book_id": "BOOK005",
            "title": "The Catcher in the Rye",
            "author": "J.D. Salinger",
            "publisher": "Little, Brown",
            "year": 1951,
            "category": "Fiction",
            "isbn": "978-0316769174",
            "quantity": 3,
            "available_quantity": 1,
            "status": "Available",
            "created_at": datetime.utcnow(),
            "is_active": True
        },
        {
            "book_id": "BOOK006",
            "title": "The Hobbit",
            "author": "J.R.R. Tolkien",
            "publisher": "Allen & Unwin",
            "year": 1937,
            "category": "Fantasy",
            "isbn": "978-0547928227",
            "quantity": 4,
            "available_quantity": 0,
            "status": "Unavailable",
            "created_at": datetime.utcnow(),
            "is_active": True
        },
        {
            "book_id": "BOOK007",
            "title": "Python Programming",
            "author": "Guido van Rossum",
            "publisher": "O'Reilly",
            "year": 2019,
            "category": "Programming",
            "isbn": "978-1492051367",
            "quantity": 6,
            "available_quantity": 6,
            "status": "Available",
            "created_at": datetime.utcnow(),
            "is_active": True
        },
        {
            "book_id": "BOOK008",
            "title": "Clean Code",
            "author": "Robert C. Martin",
            "publisher": "Prentice Hall",
            "year": 2008,
            "category": "Programming",
            "isbn": "978-0132350884",
            "quantity": 3,
            "available_quantity": 3,
            "status": "Available",
            "created_at": datetime.utcnow(),
            "is_active": True
        }
    ]
    
    try:
        result = books_collection.insert_many(sample_books)
        print(f"[+] {len(result.inserted_ids)} sample books seeded to database")
    except Exception as e:
        print(f"[-] Error seeding books: {e}")


