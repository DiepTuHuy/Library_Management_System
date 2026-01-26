"""
Role-based access control utilities for controllers
"""

def require_role(*allowed_roles):
    """Decorator to check if user has required role"""
    def decorator(func):
        def wrapper(self, user_id, *args, **kwargs):
            # This would need to be integrated with actual user session/context
            # For now, it's a template for how role-based access could work
            return func(self, user_id, *args, **kwargs)
        return wrapper
    return decorator

def check_user_role(db, user_id, required_roles):
    """Check if user has one of the required roles"""
    from models.user import User
    from bson.objectid import ObjectId
    
    if isinstance(user_id, str):
        user_id = ObjectId(user_id)
    
    user = User.get_by_id(db, user_id)
    if not user:
        return False
    
    return user.role in required_roles

def require_admin(user_role):
    """Check if user is admin"""
    return user_role == "admin"

def require_librarian_or_admin(user_role):
    """Check if user is librarian or admin"""
    return user_role in ["librarian", "admin"]

def require_member_or_above(user_role):
    """Check if user is at least a member"""
    return user_role in ["member", "librarian", "admin"]
