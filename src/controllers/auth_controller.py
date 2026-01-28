"""
Authentication Controller
Handles authentication requests using MongoDB database lookup
All users (admin, librarian, member) authenticated from database
"""

from ..services.user_service import UserService
from ..models.database import get_db


class AuthController:
    """Controller for authentication operations"""
    
    def __init__(self):
        """Initialize auth controller"""
        self.db = get_db()
        self.user_service = UserService()
    
    def login(self, email, password):
        """
        Authenticate user from MongoDB database
        Unified authentication for all roles
        
        Args:
            email (str): User email
            password (str): User password
        
        Returns:
            dict: {
                "success": bool,
                "user": {
                    "_id": str,
                    "name": str,
                    "email": str,
                    "role": str (admin|librarian|member)
                },
                "message": str
            }
        """
        return self.user_service.authenticate_user(email, password)
    
    def register(self, name, email, password):
        """
        Register new user in MongoDB
        Default role is 'member'
        
        Args:
            name (str): Full name
            email (str): Email
            password (str): Password
        
        Returns:
            dict: {
                "success": bool,
                "user_id": str (if successful),
                "message": str
            }
        """
        return self.user_service.create_user(name, email, password, role="member")
    
    def change_password(self, email, old_password, new_password):
        """
        Change user password
        
        Args:
            email (str): User email
            old_password (str): Current password
            new_password (str): New password
        
        Returns:
            dict: {success: bool, message: str}
        """
        return self.user_service.update_password(email, old_password, new_password)
    
    def get_user(self, email):
        """Get user by email"""
        user = self.user_service.get_user_by_email(email)
        if user:
            return {
                "success": True,
                "user": {
                    "_id": str(user._id),
                    "name": user.name,
                    "email": user.email,
                    "role": user.role
                }
            }
        return {"success": False, "message": "User not found"}
    
    def get_user_profile(self, user_id):
        """Get user's complete profile including optional fields"""
        return self.user_service.get_user_profile(user_id)
    
    def update_user_profile(self, user_id, **kwargs):
        """Update user's profile with optional fields"""
        return self.user_service.update_user_profile(user_id, **kwargs)
    
    def get_all_users(self):
        """Get all registered users (Admin only)"""
        return self.user_service.get_all_users()
    
    def delete_user(self, user_id):
        """Delete a user by ID (Admin only)"""
        return self.user_service.delete_user(user_id)


