from bson import ObjectId
from datetime import datetime
from models.database import get_db
import hashlib
import secrets


class User:
    @staticmethod
    def hash_password(password):
        """Hash password using SHA-256 with salt"""
        salt = secrets.token_hex(16)
        hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}${hashed.hex()}"
    
    @staticmethod
    def verify_password(stored_hash, provided_password):
        """Verify password against stored hash"""
        try:
            salt, hashed = stored_hash.split('$')
            provided_hash = hashlib.pbkdf2_hmac('sha256', provided_password.encode(), salt.encode(), 100000)
            return provided_hash.hex() == hashed
        except:
            return False

    def __init__(self, name, email, password, role="member", user_id=None):
        self._id = user_id
        self.name = name
        self.email = email
        # Hash password on initialization
        self.password = self.hash_password(password) if not user_id else password
        self.role = role  # admin, librarian, member
        self.created_at = datetime.utcnow()
        self.is_active = True

    def save(self, db):
        """Save or update user in database"""
        try:
            user_dict = {
                "name": self.name,
                "email": self.email,
                "password": self.password,
                "role": self.role,
                "created_at": self.created_at,
                "is_active": self.is_active,
            }
            if self._id:
                db["users"].update_one({"_id": self._id}, {"$set": user_dict})
            else:
                result = db["users"].insert_one(user_dict)
                self._id = result.inserted_id
            return True
        except Exception as e:
            print(f"Error saving user: {e}")
            return False

    def delete(self, db):
        """Soft delete user"""
        try:
            self.is_active = False
            return self.save(db)
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False

    @staticmethod
    def get_by_id(db, user_id):
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        user_dict = db["users"].find_one({"_id": user_id})
        if user_dict:
            return User._dict_to_user(user_dict)
        return None

    @staticmethod
    def get_by_email(db, email):
        user_dict = db["users"].find_one({"email": email, "is_active": True})
        if user_dict:
            return User._dict_to_user(user_dict)
        return None

    @staticmethod
    def get_all(db, role=None):
        """Get all active users, optionally filtered by role"""
        try:
            query = {"is_active": True}
            if role:
                query["role"] = role
            users = []
            for user_dict in db["users"].find(query):
                users.append(User._dict_to_user(user_dict))
            return users
        except Exception as e:
            print(f"Error getting users: {e}")
            return []

    @staticmethod
    def authenticate(db, email, password):
        """Authenticate user with email and password"""
        user = User.get_by_email(db, email)
        if user and User.verify_password(user.password, password):
            return user
        return None

    # Users → BorrowRecords (1-n)
    @staticmethod
    def get_borrow_records(db, user_id):
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        return list(db["borrow_records"].find({"user_id": user_id}))

    @staticmethod
    def get_active_borrows(db, user_id):
        """Get all active (not returned) borrow records for user"""
        if isinstance(user_id, str):
            user_id = ObjectId(user_id)
        return list(
            db["borrow_records"].find(
                {"user_id": user_id, "return_date": None}
            )
        )

    @staticmethod
    def _dict_to_user(user_dict):
        """Convert dict to User object"""
        user = User(
            name=user_dict.get("name", ""),
            email=user_dict.get("email", ""),
            password=user_dict.get("password", ""),
            role=user_dict.get("role", "member"),
            user_id=user_dict.get("_id"),
        )
        user.created_at = user_dict.get("created_at")
        user.is_active = user_dict.get("is_active", True)
        return user
