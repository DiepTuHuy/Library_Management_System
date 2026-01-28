"""
Script to create test member accounts with borrow records
- Member 1: Returns book on time
- Member 2: Returns book late
"""

from pymongo import MongoClient
from datetime import datetime, timedelta
from bson import ObjectId
import hashlib
import secrets

# MongoDB connection
MONGODB_URI = "mongodb+srv://dieptuhuy80:Hitori123@lms.wpuvhhb.mongodb.net/library_db"
client = MongoClient(MONGODB_URI)
db = client["LMD_DB"]

def hash_password(password):
    """Hash password using PBKDF2 with salt (same as User model)"""
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}${hashed.hex()}"

def create_test_members():
    """Create 2 test member accounts with borrow records"""
    
    users_collection = db["users"]
    books_collection = db["books"]
    borrows_collection = db["borrow_records"]
    
    print("\n" + "="*80)
    print("CREATING TEST MEMBER ACCOUNTS")
    print("="*80)
    
    # ===== MEMBER 1: Returns book on time =====
    member1_data = {
        "name": "Nguyễn Văn Trả Đúng",
        "email": "member.ontime@library.test",
        "password": hash_password("member123"),
        "role": "member",
        "phone": "0901234567",
        "address": "123 Đường Trả Đúng, TP HCM",
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    # Check if member 1 exists
    if not users_collection.find_one({"email": member1_data["email"]}):
        member1_result = users_collection.insert_one(member1_data)
        member1_id = member1_result.inserted_id
        print(f"✅ Created Member 1: {member1_data['name']} (ID: {member1_id})")
        print(f"   Email: {member1_data['email']}")
        print(f"   Password: member123")
    else:
        member1 = users_collection.find_one({"email": member1_data["email"]})
        member1_id = member1["_id"]
        print(f"✅ Member 1 already exists: {member1_data['name']}")
    
    # ===== MEMBER 2: Returns book late =====
    member2_data = {
        "name": "Trần Thị Trả Muộn",
        "email": "member.late@library.test",
        "password": hash_password("member123"),
        "role": "member",
        "phone": "0912345678",
        "address": "456 Đường Trả Muộn, TP HCM",
        "created_at": datetime.utcnow(),
        "is_active": True
    }
    
    # Check if member 2 exists
    if not users_collection.find_one({"email": member2_data["email"]}):
        member2_result = users_collection.insert_one(member2_data)
        member2_id = member2_result.inserted_id
        print(f"✅ Created Member 2: {member2_data['name']} (ID: {member2_id})")
        print(f"   Email: {member2_data['email']}")
        print(f"   Password: member123")
    else:
        member2 = users_collection.find_one({"email": member2_data["email"]})
        member2_id = member2["_id"]
        print(f"✅ Member 2 already exists: {member2_data['name']}")
    
    # Get some books to borrow
    books = list(books_collection.find({"is_active": True}).limit(2))
    if len(books) < 2:
        print("\n❌ ERROR: Need at least 2 books in database!")
        return False
    
    book1 = books[0]
    book2 = books[1]
    
    print(f"\n📚 Using books for borrow records:")
    print(f"   Book 1: {book1.get('title')} (ID: {book1.get('book_id')})")
    print(f"   Book 2: {book2.get('title')} (ID: {book2.get('book_id')})")
    
    # ===== BORROW RECORD 1: ON TIME RETURN =====
    # Borrow: 15 days ago, Due: 7 days ago, Returned: 7 days ago (before due date)
    borrow1_date = datetime.utcnow() - timedelta(days=15)
    due1_date = borrow1_date + timedelta(days=14)  # Default 14 day borrow period
    return1_date = due1_date - timedelta(days=1)  # Return 1 day before due date (ON TIME)
    
    borrow1_record = {
        "user_id": member1_id,
        "book_id": book1.get("book_id"),
        "borrow_date": borrow1_date,
        "due_date": due1_date,
        "return_date": return1_date,
        "fine_id": None,
        "is_active": True
    }
    
    # Check if already exists
    existing_borrow1 = borrows_collection.find_one({
        "user_id": member1_id,
        "book_id": book1.get("book_id"),
        "return_date": {"$exists": True}
    })
    
    if not existing_borrow1:
        borrow1_result = borrows_collection.insert_one(borrow1_record)
        print(f"\n✅ Created Borrow Record 1 (ON TIME):")
        print(f"   Member: {member1_data['name']}")
        print(f"   Book: {book1.get('title')}")
        print(f"   Borrow Date: {borrow1_date.strftime('%Y-%m-%d')}")
        print(f"   Due Date: {due1_date.strftime('%Y-%m-%d')}")
        print(f"   Return Date: {return1_date.strftime('%Y-%m-%d')} ✅ (Before due date)")
    else:
        print(f"\n✅ Borrow Record 1 already exists (ON TIME)")
    
    # ===== BORROW RECORD 2: LATE RETURN =====
    # Borrow: 20 days ago, Due: 6 days ago, Returned: 2 days ago (after due date = LATE)
    borrow2_date = datetime.utcnow() - timedelta(days=20)
    due2_date = borrow2_date + timedelta(days=14)  # Default 14 day borrow period
    return2_date = due2_date + timedelta(days=4)   # Return 4 days after due date (LATE)
    
    borrow2_record = {
        "user_id": member2_id,
        "book_id": book2.get("book_id"),
        "borrow_date": borrow2_date,
        "due_date": due2_date,
        "return_date": return2_date,
        "fine_id": None,
        "is_active": True
    }
    
    # Check if already exists
    existing_borrow2 = borrows_collection.find_one({
        "user_id": member2_id,
        "book_id": book2.get("book_id"),
        "return_date": {"$exists": True}
    })
    
    if not existing_borrow2:
        borrow2_result = borrows_collection.insert_one(borrow2_record)
        overdue_days = (return2_date - due2_date).days
        print(f"\n✅ Created Borrow Record 2 (LATE RETURN):")
        print(f"   Member: {member2_data['name']}")
        print(f"   Book: {book2.get('title')}")
        print(f"   Borrow Date: {borrow2_date.strftime('%Y-%m-%d')}")
        print(f"   Due Date: {due2_date.strftime('%Y-%m-%d')}")
        print(f"   Return Date: {return2_date.strftime('%Y-%m-%d')} ❌ (After due date - {overdue_days} days late)")
    else:
        print(f"\n✅ Borrow Record 2 already exists (LATE RETURN)")
    
    # ===== SUMMARY =====
    print("\n" + "="*80)
    print("TEST DATA SUMMARY")
    print("="*80)
    print("\n📋 Member 1 (On Time Return):")
    print(f"   Email: member.ontime@library.test")
    print(f"   Password: member123")
    print(f"   Name: Nguyễn Văn Trả Đúng")
    print(f"   Status: Returned book on time ✅")
    
    print("\n📋 Member 2 (Late Return):")
    print(f"   Email: member.late@library.test")
    print(f"   Password: member123")
    print(f"   Name: Trần Thị Trả Muộn")
    print(f"   Status: Returned book 4 days late ❌")
    
    print("\n✨ Test data creation complete!\n")
    return True

if __name__ == "__main__":
    try:
        success = create_test_members()
        if success:
            print("✅ All test members created successfully!")
        else:
            print("❌ Failed to create test members")
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
