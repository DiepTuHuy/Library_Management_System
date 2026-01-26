"""
Authentication Controller
Handles authentication for different user roles: Admin, Librarian, and Member
"""

from models.user import User
from models.database import get_db
import hashlib


class AuthController:
    """Controller for authentication operations"""
    
    # Hardcoded admin credentials
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "admin123"
    
    # Hardcoded librarian credentials
    LIBRARIAN_USERNAME = "librarian"
    LIBRARIAN_PASSWORD = "librarian123"
    
    def __init__(self):
        """Initialize auth controller"""
        self.db = get_db()
    
    def set_db(self, db):
        """Set database instance for testing"""
        self.db = db
    
    @staticmethod
    def hash_password(password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate_admin(self, username, password):
        """
        Authenticate admin user
        
        Args:
            username (str): Admin username
            password (str): Admin password
        
        Returns:
            dict: Authentication result
        """
        try:
            if username == self.ADMIN_USERNAME and password == self.ADMIN_PASSWORD:
                return {
                    "success": True,
                    "message": "Admin authenticated successfully",
                    "user": {
                        "_id": "admin",
                        "username": self.ADMIN_USERNAME,
                        "role": "admin",
                        "name": "Administrator"
                    }
                }
            else:
                return {
                    "success": False,
                    "message": "Invalid admin credentials"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error authenticating admin: {str(e)}"
            }
    
    def authenticate_librarian(self, username, password):
        """
        Authenticate librarian user
        
        Args:
            username (str): Librarian username
            password (str): Librarian password
        
        Returns:
            dict: Authentication result
        """
        try:
            if username == self.LIBRARIAN_USERNAME and password == self.LIBRARIAN_PASSWORD:
                return {
                    "success": True,
                    "message": "Librarian authenticated successfully",
                    "user": {
                        "_id": "librarian",
                        "username": self.LIBRARIAN_USERNAME,
                        "role": "librarian",
                        "name": "Librarian"
                    }
                }
            else:
                return {
                    "success": False,
                    "message": "Invalid librarian credentials"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error authenticating librarian: {str(e)}"
            }
    
    def authenticate_member(self, email, password):
        """
        Authenticate member/student user from database
        
        Args:
            email (str): Member email
            password (str): Member password
        
        Returns:
            dict: Authentication result
        """
        try:
            # Get user from database (including inactive/deleted ones to check status)
            users_collection = self.db.get_collection("users")
            user_doc = users_collection.find_one({"email": email})
            
            if not user_doc:
                return {
                    "success": False,
                    "message": "User not found"
                }
            
            # Check if user is deleted or inactive
            if user_doc.get("is_deleted", False) or not user_doc.get("is_active", True):
                return {
                    "success": False,
                    "message": "User account is deleted or inactive"
                }
            
            # Convert doc to User object for password verification
            user = User._dict_to_user(user_doc)
            
            # Verify password using User.verify_password method
            if not User.verify_password(user.password, password):
                return {
                    "success": False,
                    "message": "Invalid password"
                }
            
            return {
                "success": True,
                "message": "Member authenticated successfully",
                "user": {
                    "_id": str(user_doc.get("_id")),
                    "email": user_doc.get("email"),
                    "name": user_doc.get("name"),
                    "role": user_doc.get("role", "member"),
                    "phone": user_doc.get("phone", ""),
                    "address": user_doc.get("address", "")
                }
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error authenticating member: {str(e)}"
            }
    
    def authenticate(self, username_or_email, password, role=None):
        """
        Universal authentication method
        Automatically determines user type and authenticates accordingly
        
        Args:
            username_or_email (str): Username or email
            password (str): Password
            role (str, optional): User role ('admin', 'librarian', 'member')
        
        Returns:
            dict: Authentication result
        """
        try:
            # If role is specified, use that
            if role:
                if role == "admin":
                    return self.authenticate_admin(username_or_email, password)
                elif role == "librarian":
                    return self.authenticate_librarian(username_or_email, password)
                elif role == "member":
                    return self.authenticate_member(username_or_email, password)
                else:
                    return {
                        "success": False,
                        "message": f"Unknown role: {role}"
                    }
            
            # Try admin first
            if username_or_email == self.ADMIN_USERNAME:
                return self.authenticate_admin(username_or_email, password)
            
            # Try librarian
            if username_or_email == self.LIBRARIAN_USERNAME:
                return self.authenticate_librarian(username_or_email, password)
            
            # Otherwise try as member (assume email)
            return self.authenticate_member(username_or_email, password)
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Authentication error: {str(e)}"
            }
    
    def get_user_role(self, username_or_email):
        """
        Determine user role without authentication
        
        Args:
            username_or_email (str): Username or email
        
        Returns:
            str: User role ('admin', 'librarian', 'member', or None)
        """
        try:
            if username_or_email == self.ADMIN_USERNAME:
                return "admin"
            elif username_or_email == self.LIBRARIAN_USERNAME:
                return "librarian"
            else:
                # Check if email exists in database as member
                users_collection = self.db.get_collection("users")
                user_doc = users_collection.find_one({"email": username_or_email})
                if user_doc:
                    return user_doc.get("role", "member")
                return None
        except Exception as e:
            return None
    
    def change_member_password(self, email, old_password, new_password):
        """
        Change member password
        
        Args:
            email (str): Member email
            old_password (str): Old password
            new_password (str): New password
        
        Returns:
            dict: Operation result
        """
        try:
            # Verify old password first
            auth_result = self.authenticate_member(email, old_password)
            if not auth_result["success"]:
                return {
                    "success": False,
                    "message": "Invalid current password"
                }
            
            # Get user and update with hashed new password
            user = User.get_by_email(self.db, email)
            if not user:
                return {
                    "success": False,
                    "message": "User not found"
                }
            
            # Hash new password
            user.password = User.hash_password(new_password)
            
            # Save updated user
            if user.save(self.db):
                return {
                    "success": True,
                    "message": "Password changed successfully"
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to update password"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error changing password: {str(e)}"
            }
    
    def validate_credentials_format(self, username_or_email, password):
        """
        Validate credentials format
        
        Args:
            username_or_email (str): Username or email
            password (str): Password
        
        Returns:
            dict: Validation result
        """
        try:
            if not username_or_email or not isinstance(username_or_email, str):
                return {
                    "valid": False,
                    "message": "Username/email is required"
                }
            
            if not password or not isinstance(password, str):
                return {
                    "valid": False,
                    "message": "Password is required"
                }
            
            if len(password) < 6:
                return {
                    "valid": False,
                    "message": "Password must be at least 6 characters"
                }
            
            return {
                "valid": True,
                "message": "Credentials format is valid"
            }
        except Exception as e:
            return {
                "valid": False,
                "message": f"Error validating credentials: {str(e)}"
            }
