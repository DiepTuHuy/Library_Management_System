from pymongo import MongoClient
from ..models.user import User
from ..models.database import get_db


class UserService:
    """Service layer for user operations"""
    
    def __init__(self):
        self.db = get_db()
    
    def authenticate_user(self, email, password):
        """
        Authenticate user using email and password from MongoDB
        Unified authentication for all roles (admin, librarian, member)
        
        Args:
            email (str): User email
            password (str): User password
        
        Returns:
            dict: {
                "success": bool,
                "user": {...user data...},
                "message": str
            }
        """
        try:
            # Query database for user by email
            user = User.authenticate(self.db, email, password)
            
            if user:
                return {
                    "success": True,
                    "user": {
                        "_id": str(user._id),
                        "name": user.name,
                        "email": user.email,
                        "role": user.role
                    },
                    "message": f"{user.role.capitalize()} authenticated successfully"
                }
            else:
                return {
                    "success": False,
                    "message": "Invalid email or password"
                }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"Authentication error: {str(e)}"
            }
    
    def get_user_by_email(self, email):
        """Get user by email from database"""
        return User.get_by_email(self.db, email)
    
    def get_user_by_id(self, user_id):
        """Get user by ID from database"""
        return User.get_by_id(self.db, user_id)
    
    def get_users_by_role(self, role):
        """Get all users of a specific role"""
        return User.get_all(self.db, role=role)
    
    def create_user(self, name, email, password, role="member"):
        """
        Create new user in database
        
        Args:
            name (str): User full name
            email (str): User email
            password (str): User password (will be hashed)
            role (str): User role (member, librarian, admin)
        
        Returns:
            dict: {
                "success": bool,
                "message": str,
                "user_id": str (if successful)
            }
        """
        try:
            # Check if email already exists
            if User.get_by_email(self.db, email):
                return {"success": False, "message": "Email already exists"}
            
            if len(password) < 6:
                return {"success": False, "message": "Password must be at least 6 characters"}
            
            user = User(name=name, email=email, password=password, role=role)
            if user.save(self.db):
                return {
                    "success": True,
                    "message": "User created successfully",
                    "user_id": str(user._id)
                }
            else:
                return {"success": False, "message": "Failed to create user"}
        
        except Exception as e:
            return {"success": False, "message": f"Error creating user: {str(e)}"}
    
    def update_password(self, email, old_password, new_password):
        """
        Update user password
        
        Args:
            email (str): User email
            old_password (str): Current password
            new_password (str): New password
        
        Returns:
            dict: {success: bool, message: str}
        """
        try:
            # Verify old password first
            auth_result = self.authenticate_user(email, old_password)
            if not auth_result["success"]:
                return {"success": False, "message": "Invalid current password"}
            
            # Get user and update password
            user = User.get_by_email(self.db, email)
            if not user:
                return {"success": False, "message": "User not found"}
            
            # Hash and save new password
            user.password = User.hash_password(new_password)
            if user.save(self.db):
                return {"success": True, "message": "Password updated successfully"}
            else:
                return {"success": False, "message": "Failed to update password"}
        
        except Exception as e:
            return {"success": False, "message": f"Error updating password: {str(e)}"}
    
    def delete_user(self, email):
        """Soft delete user (mark as inactive)"""
        try:
            user = User.get_by_email(self.db, email)
            if not user:
                return {"success": False, "message": "User not found"}
            
            if user.delete(self.db):
                return {"success": True, "message": "User deleted successfully"}
            else:
                return {"success": False, "message": "Failed to delete user"}
        
        except Exception as e:
            return {"success": False, "message": f"Error deleting user: {str(e)}"}
    
    def get_user_profile(self, user_id):
        """
        Get complete user profile including optional fields
        
        Args:
            user_id (str): User ID (MongoDB ObjectId)
        
        Returns:
            dict: {
                "success": bool,
                "profile": {...profile data...},
                "message": str
            }
        """
        try:
            user = User.get_by_id(self.db, user_id)
            if not user:
                return {"success": False, "message": "User not found"}
            
            profile = {
                "_id": str(user._id),
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "address": user.address,
                "gender": user.gender,
                "phone_number": user.phone_number,
                "date_of_birth": user.date_of_birth,
            }
            
            return {"success": True, "profile": profile}
        
        except Exception as e:
            return {"success": False, "message": f"Error fetching profile: {str(e)}"}
    
    def update_user_profile(self, user_id, **kwargs):
        """
        Update user profile with optional fields
        Only allows updating: address, gender, phone_number, date_of_birth
        Name and email can only be updated through specific methods
        
        Args:
            user_id (str): User ID (MongoDB ObjectId)
            **kwargs: Optional fields to update
                - address (str)
                - gender (str)
                - phone_number (str)
                - date_of_birth (str)
        
        Returns:
            dict: {
                "success": bool,
                "profile": {...updated profile...},
                "message": str
            }
        """
        try:
            user = User.get_by_id(self.db, user_id)
            if not user:
                return {"success": False, "message": "User not found"}
            
            # Only allow updating specific optional fields
            allowed_fields = ['address', 'gender', 'phone_number', 'date_of_birth']
            
            for field in allowed_fields:
                if field in kwargs and kwargs[field] is not None:
                    setattr(user, field, kwargs[field])
            
            if user.save(self.db):
                profile = {
                    "_id": str(user._id),
                    "name": user.name,
                    "email": user.email,
                    "role": user.role,
                    "created_at": user.created_at.isoformat() if user.created_at else None,
                    "address": user.address,
                    "gender": user.gender,
                    "phone_number": user.phone_number,
                    "date_of_birth": user.date_of_birth,
                }
                return {
                    "success": True,
                    "profile": profile,
                    "message": "Profile updated successfully"
                }
            else:
                return {"success": False, "message": "Failed to update profile"}
        
        except Exception as e:
            return {"success": False, "message": f"Error updating profile: {str(e)}"}
    
    def get_all_users(self):
        """Get all registered users (members only, excluding admin and librarian)"""
        try:
            users = User.get_all(self.db, role="member", include_inactive=True)
            
            user_list = []
            for user in users:
                user_list.append({
                    "_id": str(user._id),
                    "name": user.name,
                    "email": user.email,
                    "role": user.role,
                    "created_at": user.created_at.isoformat() if user.created_at else None
                })
            
            return {
                "success": True,
                "users": user_list,
                "count": len(user_list),
                "message": f"Retrieved {len(user_list)} members"
            }
        except Exception as e:
            return {"success": False, "message": f"Error retrieving users: {str(e)}"}
    
    def delete_user(self, user_id):
        """Delete a user by ID"""
        try:
            user = User.get_by_id(self.db, user_id)
            if not user:
                return {"success": False, "message": "User not found"}
            
            # Don't allow deleting admin users
            if user.role == "admin":
                return {"success": False, "message": "Cannot delete admin users"}
            
            if user.delete(self.db):
                return {"success": True, "message": f"User {user.email} deleted successfully"}
            else:
                return {"success": False, "message": "Failed to delete user"}
        except Exception as e:
            return {"success": False, "message": f"Error deleting user: {str(e)}"}


# Legacy support functions
client = MongoClient("mongodb+srv://dieptuhuy80:Hitori123@lms.wpuvhhb.mongodb.net/library_db")
db = client["LMD_DB"]
user_col = db["User"]

def get_next_user_id():
    last = user_col.find_one(sort=[("_id", -1)])
    return (last["_id"] + 1) if last else 1

def register_user(username, password, full_name, email):
    if user_col.find_one({"username": username}):
        return False, "Username đã tồn tại"

    new_user = {
        "_id": get_next_user_id(),
        "username": username,
        "user_password": password,
        "full_name": full_name,
        "email": email,
        "user_role": "USER",
        "is_active": True
    }

    user_col.insert_one(new_user)
    return True, "Đăng ký thành công"