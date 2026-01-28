from ..models.user import User
from ..models.database import get_db
from bson.objectid import ObjectId


class UserController:
    """Controller for user management operations"""

    def __init__(self):
        self.db = get_db()

    def register_user(self, name, email, password, role="member"):
        """Register a new user"""
        try:
            # Check if email already exists
            if User.get_by_email(self.db, email):
                return {"success": False, "message": "Email already exists"}

            user = User(name=name, email=email, password=password, role=role)
            if user.save(self.db):
                return {
                    "success": True,
                    "message": "User registered successfully",
                    "user_id": str(user._id),
                }
            else:
                return {"success": False, "message": "Failed to register user"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def login(self, email, password):
        """Authenticate user"""
        try:
            user = User.authenticate(self.db, email, password)
            if user:
                return {
                    "success": True,
                    "message": "Login successful",
                    "user": {
                        "id": str(user._id),
                        "name": user.name,
                        "email": user.email,
                        "role": user.role,
                    },
                }
            else:
                return {"success": False, "message": "Invalid email or password"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_user(self, user_id):
        """Get user details"""
        try:
            user = User.get_by_id(self.db, user_id)
            if not user:
                return {"success": False, "message": "User not found"}

            return {
                "success": True,
                "user": {
                    "id": str(user._id),
                    "name": user.name,
                    "email": user.email,
                    "role": user.role,
                    "created_at": user.created_at.isoformat(),
                    "is_active": user.is_active,
                },
            }
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_all_users(self, role=None):
        """Get all users, optionally filtered by role"""
        try:
            users = User.get_all(self.db, role=role)
            users_data = []
            for user in users:
                users_data.append(
                    {
                        "id": str(user._id),
                        "name": user.name,
                        "email": user.email,
                        "role": user.role,
                        "created_at": user.created_at.isoformat(),
                    }
                )
            return {
                "success": True,
                "users": users_data,
                "count": len(users_data),
            }
        except Exception as e:
            return {"success": False, "message": str(e), "users": [], "count": 0}

    def update_user(self, user_id, **kwargs):
        """Update user information"""
        try:
            user = User.get_by_id(self.db, user_id)
            if not user:
                return {"success": False, "message": "User not found"}

            for key, value in kwargs.items():
                if hasattr(user, key) and key not in ["_id", "created_at"]:
                    setattr(user, key, value)

            if user.save(self.db):
                return {
                    "success": True,
                    "message": "User updated successfully",
                }
            else:
                return {"success": False, "message": "Failed to update user"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def delete_user(self, user_id):
        """Delete (deactivate) user"""
        try:
            user = User.get_by_id(self.db, user_id)
            if not user:
                return {"success": False, "message": "User not found"}

            if user.delete(self.db):
                return {"success": True, "message": "User deleted successfully"}
            else:
                return {"success": False, "message": "Failed to delete user"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    def get_user_borrow_records(self, user_id):
        """Get all borrow records for user"""
        try:
            records = User.get_borrow_records(self.db, user_id)
            records_data = []
            for record in records:
                records_data.append({
                    "id": str(record.get("_id")),
                    "book_id": str(record.get("book_id")),
                    "borrow_date": record.get("borrow_date").isoformat() if record.get("borrow_date") else None,
                    "due_date": record.get("due_date").isoformat() if record.get("due_date") else None,
                    "return_date": record.get("return_date").isoformat() if record.get("return_date") else None,
                })
            return {
                "success": True,
                "records": records_data,
                "count": len(records_data),
            }
        except Exception as e:
            return {"success": False, "message": str(e), "records": [], "count": 0}

    def get_active_borrows(self, user_id):
        """Get all active borrow records for user"""
        try:
            records = User.get_active_borrows(self.db, user_id)
            records_data = []
            for record in records:
                records_data.append({
                    "id": str(record.get("_id")),
                    "book_id": str(record.get("book_id")),
                    "borrow_date": record.get("borrow_date").isoformat(),
                    "due_date": record.get("due_date").isoformat(),
                })
            return {
                "success": True,
                "records": records_data,
                "count": len(records_data),
            }
        except Exception as e:
            return {"success": False, "message": str(e), "records": [], "count": 0}
